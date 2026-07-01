
# ═══════════════════════════════════════════════════════
# DB CONFIG — Fixed Version
# Lazy loading use karta hai
# Environment variables runtime pe read hoti hain
# Module import time pe nahi!
# ═══════════════════════════════════════════════════════

import os
import logging

log = logging.getLogger("MentorMind")


def get_db_type() -> str:
    """
    DB_TYPE runtime pe read karo.
    Import time pe nahi — isliye caching problem nahi!
    """
    return os.environ.get("DB_TYPE", "sqlite").lower()


def get_postgres_url() -> str:
    """PostgreSQL URL runtime pe read karo."""
    url = os.environ.get("DATABASE_URL", "")
    # Render/Heroku sometimes give postgres:// prefix
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_sqlite_url() -> str:
    """SQLite URL banao."""
    path = os.environ.get("SQLITE_PATH", "mentor_mind.db")
    return f"sqlite:///{path}"


def get_database_url() -> str:
    """
    Active database URL return karo.
    Har baar call pe fresh environment read karta hai.
    """
    db_type      = get_db_type()
    postgres_url = get_postgres_url()

    if db_type == "postgresql" and postgres_url:
        log.info("Database: PostgreSQL (Supabase)")
        return postgres_url

    log.info("Database: SQLite (local)")
    return get_sqlite_url()


# ── These are read ONCE at import time ────────────────
# Only non-critical settings here
POOL_SIZE    = int(os.environ.get("DB_POOL_SIZE",   "5"))
MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW","10"))
POOL_TIMEOUT = int(os.environ.get("DB_POOL_TIMEOUT","30"))
ECHO_SQL     = os.environ.get("DB_ECHO","false").lower() == "true"
