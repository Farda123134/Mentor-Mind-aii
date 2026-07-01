import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm  import sessionmaker
from sqlalchemy.pool import StaticPool, NullPool

from .db_config import get_database_url, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, ECHO_SQL
from .models import Base

log = logging.getLogger("MentorMind")

_engine       = None
_SessionLocal = None


def _create_engine_for_url(url: str):
    if "sqlite" in url:
        eng = create_engine(
            url,
            connect_args = {"check_same_thread": False},
            poolclass    = StaticPool,
            echo         = ECHO_SQL
        )

        @event.listens_for(eng, "connect")
        def set_sqlite_pragma(dbapi_conn, conn_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        log.info("SQLite engine created: " + url)
        return eng
    else:
        eng = create_engine(
            url,
            poolclass    = NullPool,
            echo         = ECHO_SQL,
            connect_args = {
                "connect_timeout"    : 10,
                "keepalives"         : 1,
                "keepalives_idle"    : 30,
                "keepalives_interval": 5,
                "keepalives_count"   : 3,
                "sslmode"            : "require",
            }
        )
        log.info("PostgreSQL engine created: " + url[:40] + "...")
        return eng


def get_engine():
    """Engine return karo — lazy, cached, auto-switches on URL change."""
    global _engine, _SessionLocal

    current_url = get_database_url()

    if _engine is None:
        _engine       = _create_engine_for_url(current_url)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    else:
        existing_url = str(_engine.url)
        if "sqlite" in existing_url and "postgresql" in current_url:
            log.info("Database URL changed! Recreating engine...")
            _engine.dispose()
            _engine       = _create_engine_for_url(current_url)
            _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    return _engine, _SessionLocal


def init_database():
    try:
        eng, _ = get_engine()
        Base.metadata.create_all(bind=eng)
        url     = str(eng.url)
        db_type = "PostgreSQL" if "postgresql" in url else "SQLite"
        log.info("Tables ready on " + db_type)
        return True
    except Exception as e:
        log.error("Database init failed: " + str(e))
        raise


@contextmanager
def get_db_session():
    eng, SessionLocal = get_engine()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        log.error("Session error: " + str(e))
        raise
    finally:
        session.close()


def get_db():
    eng, SessionLocal = get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> dict:
    try:
        eng, _ = get_engine()
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        url     = str(eng.url)
        db_type = "postgresql" if "postgresql" in url else "sqlite"
        return {"status": "connected", "type": db_type, "url": url[:50] + "..."}
    except Exception as e:
        try:
            url = str(_engine.url) if _engine else "unknown"
        except:
            url = "unknown"
        return {"status": "error", "type": "unknown", "url": url[:50] + "...", "error": str(e)}


def reset_engine():
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
        log.info("Engine disposed")
    _engine       = None
    _SessionLocal = None
    log.info("Engine reset complete")


# ── BACKWARD COMPATIBILITY ────────────────────────────
# Kuch purana code 'from .engine import engine' use karta hai
# Yeh module-level attribute access ko proper banata hai
class _EngineProxy:
    """
    Proxy object jo 'engine' attribute access pe
    asli engine return karta hai — lazy!
    Isse 'from mentor_mind.database.engine import engine'
    bhi kaam karega.
    """
    def __getattr__(self, name):
        eng, _ = get_engine()
        return getattr(eng, name)

    def __call__(self, *args, **kwargs):
        eng, _ = get_engine()
        return eng(*args, **kwargs)


engine = _EngineProxy()
