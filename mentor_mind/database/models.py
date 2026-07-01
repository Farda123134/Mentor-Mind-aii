
from sqlalchemy import (
    Column, Integer, String, Text,
    Float, DateTime, Boolean,
    create_engine, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm              import relationship
from datetime                    import datetime

Base = declarative_base()


# ── TABLE 1: USERS ────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id          = Column(Integer,     primary_key=True, autoincrement=True)
    session_id  = Column(String(255), unique=True, nullable=False, index=True)
    name        = Column(String(100), default="Student")
    created_at  = Column(DateTime,    default=datetime.utcnow)
    last_active = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    study_plans   = relationship("StudyPlan",    back_populates="user", cascade="all, delete")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete")
    quiz_history  = relationship("QuizHistory",  back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User session={self.session_id[:8]}>"


# ── TABLE 2: STUDY PLANS ──────────────────────────────
class StudyPlan(Base):
    __tablename__ = "study_plans"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("users.session_id"), nullable=False, index=True)
    topic      = Column(String(200), nullable=False)
    total_days = Column(Integer,     nullable=False)
    schedule   = Column(Text,        nullable=False)
    start_date = Column(String(50),  nullable=False)
    created_at = Column(DateTime,    default=datetime.utcnow)

    user     = relationship("User",     back_populates="study_plans")
    progress = relationship("Progress", back_populates="plan",
                            cascade="all, delete", uselist=False)

    def __repr__(self):
        return f"<StudyPlan topic={self.topic}>"


# ── TABLE 3: PROGRESS ─────────────────────────────────
class Progress(Base):
    __tablename__ = "progress"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False, index=True)
    topic      = Column(String(200), nullable=False)
    plan_id    = Column(Integer,     ForeignKey("study_plans.id"), nullable=True)
    completed  = Column(Text,        default="[]")
    pending    = Column(Text,        default="[]")
    percent    = Column(Float,       default=0.0)
    updated_at = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    plan = relationship("StudyPlan", back_populates="progress")

    def __repr__(self):
        return f"<Progress topic={self.topic} {self.percent}%>"


# ── TABLE 4: CONVERSATIONS ────────────────────────────
class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("users.session_id"), nullable=False, index=True)
    chat_id    = Column(String(64),  nullable=True, index=True)
    role       = Column(String(20),  nullable=False)
    message    = Column(Text,        nullable=False)
    agent_used = Column(String(100), default="")
    timestamp  = Column(DateTime,    default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation role={self.role}>"


# ── TABLE 5: QUIZ HISTORY ─────────────────────────────
class QuizHistory(Base):
    __tablename__ = "quiz_history"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    session_id = Column(String(255), ForeignKey("users.session_id"), nullable=False, index=True)
    topic      = Column(String(200), nullable=False)
    score      = Column(Integer,     default=0)
    total      = Column(Integer,     default=0)
    percentage = Column(Float,       default=0.0)
    questions  = Column(Text,        nullable=False)
    answers    = Column(Text,        nullable=False)
    taken_at   = Column(DateTime,    default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="quiz_history")

    def __repr__(self):
        return f"<QuizHistory topic={self.topic} score={self.score}/{self.total}>"


# ── TABLE 6: AUTH USERS ───────────────────────────────
class AuthUser(Base):
    __tablename__ = "auth_users"

    id            = Column(Integer,     primary_key=True, autoincrement=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    username      = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active     = Column(Boolean,     default=True)
    is_verified   = Column(Boolean,     default=False)
    created_at    = Column(DateTime,    default=datetime.utcnow)
    last_login    = Column(DateTime,    nullable=True)
    session_id    = Column(String(255), unique=True, nullable=True)

    def __repr__(self):
        return f"<AuthUser email={self.email}>"


# ── TABLE 7: AUTH TOKENS ──────────────────────────────
class AuthToken(Base):
    __tablename__ = "auth_tokens"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    user_id    = Column(Integer,     ForeignKey("auth_users.id"), nullable=False)
    token      = Column(String(500), unique=True, nullable=False, index=True)
    is_revoked = Column(Boolean,     default=False)
    created_at = Column(DateTime,    default=datetime.utcnow)
    expires_at = Column(DateTime,    nullable=False)

    def __repr__(self):
        return f"<AuthToken user_id={self.user_id}>"


# ── TABLE 8: CHAT SESSIONS (conversation grouping) ────
class ChatSession(Base):
    """
    Ek "conversation" ChatGPT jaisi.
    Har user ke multiple chat sessions ho sakte hain.
    """
    __tablename__ = "chat_sessions"

    id          = Column(Integer,     primary_key=True, autoincrement=True)
    chat_id     = Column(String(64),  unique=True, nullable=False, index=True)
    session_id  = Column(String(255), ForeignKey("users.session_id"), nullable=False, index=True)
    title       = Column(String(200), default="New Chat")
    created_at  = Column(DateTime,    default=datetime.utcnow)
    updated_at  = Column(DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted  = Column(Boolean,     default=False)

    def __repr__(self):
        return f"<ChatSession {self.title}>"
