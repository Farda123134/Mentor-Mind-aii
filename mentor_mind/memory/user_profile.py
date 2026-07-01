
# ═══════════════════════════════════════════════════════
# USER PROFILE MANAGER
# ═══════════════════════════════════════════════════════

import logging
from typing import Dict, List

log = logging.getLogger("MentorMind")


class UserProfileManager:
    """User profile aur stats manage karo."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._ensure_user()

    def _ensure_user(self):
        try:
            from mentor_mind.database.db_operations import get_or_create_user
            get_or_create_user(self.session_id)
        except Exception as e:
            log.warning(f"User ensure error: {e}")

    def get_full_profile(self) -> Dict:
        """Complete user profile nikalo."""
        try:
            from mentor_mind.database.db_operations import (
                get_all_plans, get_progress, get_quiz_history
            )
            plans    = get_all_plans(self.session_id)
            progress = {}
            for plan in plans:
                topic           = plan["topic"]
                progress[topic] = get_progress(self.session_id, topic) or {}

            quiz_history = get_quiz_history(self.session_id)
            return {
                "session_id"    : self.session_id[:8] + "...",
                "topics_studied": [p["topic"] for p in plans],
                "total_plans"   : len(plans),
                "progress"      : progress,
                "quiz_history"  : quiz_history[:5],
                "total_quizzes" : len(quiz_history)
            }
        except Exception as e:
            log.error(f"get_full_profile error: {e}")
            return {}

    def get_personalized_greeting(self) -> str:
        """User ke liye personalized greeting."""
        profile = self.get_full_profile()
        total   = profile.get("total_plans", 0)
        if total == 0:
            return "Assalam o Alaikum! Main MENTOR MIND AI hun. Aaj kya seekhna hai?"
        topics = profile.get("topics_studied", [])
        return f"Welcome back! Tumhare topics: {', '.join(topics[:2])}. Aaj kya karna hai?"

    def get_context_summary(self) -> str:
        """AI ke liye user context."""
        profile = self.get_full_profile()
        topics  = profile.get("topics_studied", [])
        if not topics:
            return "New user — no study history yet."
        progress_info = []
        for topic, prog in profile.get("progress", {}).items():
            pct = prog.get("percent", 0)
            progress_info.append(f"{topic}: {pct}%")
        return (
            f"User topics: {', '.join(topics)}\n"
            f"Progress: {', '.join(progress_info)}"
        )
