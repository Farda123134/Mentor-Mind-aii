import uuid
import logging
import bcrypt
import traceback
from datetime import datetime, timedelta
from typing   import Optional, Dict

from jose import jwt, JWTError

from mentor_mind.auth.auth_config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINS
from mentor_mind.database.engine  import get_db_session
from mentor_mind.database.models  import AuthUser, AuthToken

log = logging.getLogger("MentorMind")


def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt      = bcrypt.gensalt()
    hashed    = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            hashed.encode("utf-8")
        )
    except Exception as e:
        log.error("verify_password error: " + str(e))
        traceback.print_exc()
        return False


def create_access_token(user_id: int, email: str) -> str:
    expire  = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINS)
    payload = {
        "sub"  : str(user_id),
        "email": email,
        "exp"  : expire,
        "type" : "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    expire  = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub" : str(user_id),
        "exp" : expire,
        "type": "refresh",
        "jti" : str(uuid.uuid4())
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError as e:
        log.warning("Token invalid: " + str(e))
        return None


def register_user(email: str, password: str, username: str = "") -> Dict:
    email    = email.lower().strip()
    username = username or email.split("@")[0]

    if len(password) < 6:
        return {"success": False, "message": "Password kam se kam 6 characters ka hona chahiye"}
    if "@" not in email:
        return {"success": False, "message": "Valid email address chahiye"}

    try:
        with get_db_session() as db:
            existing = db.query(AuthUser).filter(AuthUser.email == email).first()
            if existing:
                return {"success": False, "message": "Yeh email already registered hai"}

            session_id = "user_" + uuid.uuid4().hex[:16]

            # Step 1: AuthUser banao (login/password ke liye)
            auth_user = AuthUser(
                email         = email,
                username      = username,
                password_hash = hash_password(password),
                session_id    = session_id,
                is_active     = True,
                is_verified   = True,
            )
            db.add(auth_user)
            db.flush()
            user_id = auth_user.id

            # Step 2: "users" table mein bhi entry banao
            # (chat_sessions ka Foreign Key isi table ko point karta hai)
            from mentor_mind.database.models import User
            base_user = db.query(User).filter(User.session_id == session_id).first()
            if not base_user:
                base_user = User(session_id=session_id, name=username)
                db.add(base_user)

            log.info("New user registered: " + email + " session_id: " + session_id)

        return {
            "success"   : True,
            "message"   : "Registration successful!",
            "user_id"   : user_id,
            "session_id": session_id
        }

    except Exception as e:
        log.error("register_user error: " + str(e))
        traceback.print_exc()
        return {"success": False, "message": "Registration failed: " + str(e)}


def login_user(email: str, password: str) -> Dict:
    email = email.lower().strip()

    try:
        with get_db_session() as db:
            user = db.query(AuthUser).filter(
                AuthUser.email     == email,
                AuthUser.is_active == True
            ).first()

            if not user:
                return {"success": False, "message": "Email ya password galat hai"}

            if not verify_password(password, user.password_hash):
                return {"success": False, "message": "Email ya password galat hai"}

            access_token  = create_access_token(user.id, user.email)
            refresh_token = create_refresh_token(user.id)

            db.add(AuthToken(
                user_id    = user.id,
                token      = refresh_token,
                expires_at = datetime.utcnow() + timedelta(days=7)
            ))
            user.last_login = datetime.utcnow()

            user_data = {
                "id"        : user.id,
                "email"     : user.email,
                "username"  : user.username,
                "session_id": user.session_id
            }
            log.info("User logged in: " + email)

        return {
            "success"      : True,
            "message"      : "Login successful!",
            "access_token" : access_token,
            "refresh_token": refresh_token,
            "token_type"   : "bearer",
            "user"         : user_data
        }

    except Exception as e:
        log.error("login_user error: " + str(e))
        traceback.print_exc()
        return {"success": False, "message": "Login failed: " + str(e)}


def get_current_user(token: str) -> Optional[Dict]:
    payload = verify_token(token)
    if not payload:
        return None

    user_id = int(payload.get("sub", 0))
    try:
        with get_db_session() as db:
            user = db.query(AuthUser).filter(
                AuthUser.id        == user_id,
                AuthUser.is_active == True
            ).first()
            if not user:
                return None

            # SAFETY: agar purane users ke "users" table mein entry
            # nahi hai (purane accounts jo is fix se pehle bane), to
            # yahan auto-create kar do — taake chat history kaam kare
            from mentor_mind.database.models import User
            base_user = db.query(User).filter(
                User.session_id == user.session_id
            ).first()
            if not base_user:
                base_user = User(session_id=user.session_id, name=user.username)
                db.add(base_user)
                log.info("Auto-created missing users entry for: " + user.email)

            return {
                "id"        : user.id,
                "email"     : user.email,
                "username"  : user.username,
                "session_id": user.session_id
            }
    except Exception as e:
        log.error("get_current_user error: " + str(e))
        traceback.print_exc()
        return None


def logout_user(refresh_token: str) -> Dict:
    try:
        with get_db_session() as db:
            token_record = db.query(AuthToken).filter(
                AuthToken.token      == refresh_token,
                AuthToken.is_revoked == False
            ).first()
            if token_record:
                token_record.is_revoked = True
        return {"success": True, "message": "Logout successful!"}
    except Exception as e:
        log.error("logout_user error: " + str(e))
        return {"success": False, "message": str(e)}


def change_password(user_id: int, old_password: str, new_password: str) -> Dict:
    if len(new_password) < 6:
        return {"success": False, "message": "New password kam se kam 6 characters ka hona chahiye"}
    try:
        with get_db_session() as db:
            user = db.query(AuthUser).filter(AuthUser.id == user_id).first()
            if not user:
                return {"success": False, "message": "User nahi mila"}
            if not verify_password(old_password, user.password_hash):
                return {"success": False, "message": "Purana password galat hai"}
            user.password_hash = hash_password(new_password)
            log.info("Password changed: " + user.email)
        return {"success": True, "message": "Password successfully changed!"}
    except Exception as e:
        log.error("change_password error: " + str(e))
        return {"success": False, "message": str(e)}
