
# ═══════════════════════════════════════════════════════
# PERSISTENT MEMORY
# Dictionary ki jagah SQLite database use karta hai
# Restart ke baad bhi data safe rehta hai
# ═══════════════════════════════════════════════════════

import json
import logging
from datetime import datetime
from typing   import Optional, List, Dict

log = logging.getLogger("MentorMind")


class PersistentMemory:
    """
    Production-grade memory system.

    Purani SharedMemory:  RAM mein → restart pe gone
    Nayi PersistentMemory: SQLite mein → hamesha safe

    Jaise:
    Purani: Whiteboard pe likhna (erase ho jaata)
    Nayi:   Diary mein likhna (hamesha rehta)
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self._setup_database()
        log.info(f"PersistentMemory ready — session: {session_id[:8]}")

    def _setup_database(self):
        """Database tables banao agar exist nahi karte."""
        try:
            from mentor_mind.database.db_setup import create_tables
            create_tables()
            log.info("Database tables verified")
        except Exception as e:
            log.warning(f"DB setup issue: {e}")

    # ── STUDY PLANS ───────────────────────────────────

    def save_plan(self, topic: str, plan_data: dict):
        """Study plan database mein save karo."""
        try:
            from mentor_mind.database.db_operations import save_study_plan
            save_study_plan(self.session_id, topic, plan_data)
            log.info(f"Plan saved: {topic}")
        except Exception as e:
            log.error(f"save_plan error: {e}")
            # Fallback: in-memory
            if not hasattr(self, "_plans"):
                self._plans = {}
            self._plans[topic] = plan_data

    def get_plan(self, topic: str) -> Optional[dict]:
        """Database se plan nikalo."""
        try:
            from mentor_mind.database.db_operations import get_study_plan
            return get_study_plan(self.session_id, topic)
        except Exception as e:
            log.error(f"get_plan error: {e}")
            return getattr(self, "_plans", {}).get(topic)

    @property
    def study_plans(self) -> dict:
        """
        Backward compatibility ke liye.
        Sare plans ek dict mein return karo.
        """
        try:
            from mentor_mind.database.db_operations import get_all_plans
            plans_list = get_all_plans(self.session_id)
            result     = {}
            for p in plans_list:
                full = self.get_plan(p["topic"])
                if full:
                    result[p["topic"]] = full
            return result
        except Exception as e:
            log.error(f"study_plans error: {e}")
            return getattr(self, "_plans", {})

    # ── PROGRESS ──────────────────────────────────────

    def mark_complete(self, topic: str, task: str):
        """Task complete mark karo."""
        try:
            from mentor_mind.database.db_operations import mark_task_complete
            mark_task_complete(self.session_id, topic, task)
        except Exception as e:
            log.error(f"mark_complete error: {e}")

    def get_progress_summary(self, topic: str) -> dict:
        """Progress summary nikalo."""
        try:
            from mentor_mind.database.db_operations import get_progress
            return get_progress(self.session_id, topic) or {}
        except Exception as e:
            log.error(f"get_progress_summary error: {e}")
            return {}

    def get_today_task(self, topic: str) -> Optional[str]:
        """Aaj ka task nikalo."""
        plan = self.get_plan(topic)
        if not plan:
            return None
        try:
            start  = datetime.fromisoformat(
                plan.get("start_date", datetime.now().isoformat())
            )
            day_no = (datetime.now() - start).days + 1
            for entry in plan.get("schedule", []):
                if entry.get("day") == day_no:
                    return entry.get("task")
        except Exception as e:
            log.error(f"get_today_task error: {e}")
        return None

    # ── CONVERSATION ──────────────────────────────────

    def save_conversation(self, role: str, message: str, agent: str = ""):
        """Conversation save karo."""
        try:
            from mentor_mind.database.db_operations import save_message
            save_message(self.session_id, role, message, agent)
        except Exception as e:
            log.error(f"save_conversation error: {e}")

    def get_history(self, limit: int = 10) -> List[dict]:
        """Conversation history nikalo."""
        try:
            from mentor_mind.database.db_operations import get_conversation_history
            return get_conversation_history(self.session_id, limit=limit)
        except Exception as e:
            log.error(f"get_history error: {e}")
            return []

    # ── LOGGING ───────────────────────────────────────

    def log(self, agent: str, action: str, detail: str = ""):
        """Agent activity log karo."""
        log.info(f"[{agent}] {action} — {detail}")

    def log_event(self, agent: str, action: str, detail: str = ""):
        """Alias for log (backward compatibility)."""
        self.log(agent, action, detail)
