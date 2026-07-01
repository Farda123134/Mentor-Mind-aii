
# ═══════════════════════════════════════════════════════
# DB SETUP — Updated for SQLAlchemy
# create_tables() function backward compatible hai
# ═══════════════════════════════════════════════════════

import logging
from .engine import init_database, check_db_connection

log = logging.getLogger("MentorMind")


def create_tables():
    """
    Database tables banao.
    Purana function — backward compatible.
    Ab SQLAlchemy use karta hai.
    """
    success = init_database()
    if success:
        log.info("✅ Database tables ready!")
    else:
        log.error("❌ Database setup failed!")
    return success


def get_connection():
    """
    Backward compatibility ke liye.
    New code get_db_session() use kare.
    """
    from .engine import get_db_session
    return get_db_session()


def check_database() -> dict:
    """Database health check."""
    return check_db_connection()
