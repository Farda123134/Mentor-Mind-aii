
# ═══════════════════════════════════════════════════════
# AUTH ROUTES — FastAPI endpoints
# /auth/register, /auth/login, /auth/logout, /auth/me
# ═══════════════════════════════════════════════════════

import logging
from fastapi            import APIRouter, HTTPException, Depends, Header
from fastapi.security   import HTTPBearer, HTTPAuthorizationCredentials
from pydantic           import BaseModel, EmailStr, Field
from typing             import Optional

from mentor_mind.auth.auth_service import (
    register_user, login_user,
    get_current_user, logout_user, change_password
)

log    = logging.getLogger("MentorMind")
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# ── REQUEST MODELS ────────────────────────────────────

class RegisterRequest(BaseModel):
    email    : str   = Field(..., example="student@email.com")
    password : str   = Field(..., min_length=6, example="password123")
    username : str   = Field(default="", example="Ali")

    class Config:
        json_schema_extra = {
            "example": {
                "email"   : "student@email.com",
                "password": "password123",
                "username": "Ali"
            }
        }


class LoginRequest(BaseModel):
    email    : str = Field(..., example="student@email.com")
    password : str = Field(..., example="password123")


class ChangePasswordRequest(BaseModel):
    old_password : str = Field(..., min_length=6)
    new_password : str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    refresh_token : str


# ── DEPENDENCY: Get current user ──────────────────────

async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Protected routes ke liye dependency.
    Token verify karo aur user return karo.

    Usage:
    @router.get("/protected")
    async def route(user = Depends(get_authenticated_user)):
        return {"user": user}
    """
    token = credentials.credentials
    user  = get_current_user(token)

    if not user:
        raise HTTPException(
            status_code = 401,
            detail      = "Invalid or expired token. Please login again."
        )
    return user


# ── ENDPOINTS ─────────────────────────────────────────

@router.post(
    "/register",
    summary     = "Register new user",
    description = "Naya account banao email aur password se."
)
async def register(request: RegisterRequest):
    """
    User registration.
    Email + Password → Account created → session_id milta hai
    """
    result = register_user(
        email    = request.email,
        password = request.password,
        username = request.username
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return {
        "success"   : True,
        "message"   : result["message"],
        "user_id"   : result["user_id"],
        "session_id": result["session_id"]
    }


@router.post(
    "/login",
    summary     = "Login",
    description = "Email aur password se login karo. JWT token milega."
)
async def login(request: LoginRequest):
    """
    User login.
    Returns access_token aur refresh_token.
    """
    result = login_user(
        email    = request.email,
        password = request.password
    )

    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])

    return result


@router.get(
    "/me",
    summary     = "Get current user",
    description = "Current logged-in user ki info nikalo."
)
async def get_me(user = Depends(get_authenticated_user)):
    """Current user info — token required."""
    return {
        "success": True,
        "user"   : user
    }


@router.post(
    "/logout",
    summary = "Logout"
)
async def logout(request: RefreshRequest):
    """Logout — refresh token revoke karo."""
    result = logout_user(request.refresh_token)
    return result


@router.post(
    "/change-password",
    summary = "Change password"
)
async def change_pwd(
    request : ChangePasswordRequest,
    user    = Depends(get_authenticated_user)
):
    """Password change karo — login required."""
    result = change_password(
        user_id      = user["id"],
        old_password = request.old_password,
        new_password = request.new_password
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get(
    "/verify-token",
    summary = "Verify token validity"
)
async def verify_token_endpoint(
    user = Depends(get_authenticated_user)
):
    """Token valid hai ya nahi check karo."""
    return {
        "valid"  : True,
        "user_id": user["id"],
        "email"  : user["email"]
    }
