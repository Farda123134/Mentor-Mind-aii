
# ═══════════════════════════════════════════════════════
# CONVERSATION MANAGER
# Chat history manage karta hai
# ═══════════════════════════════════════════════════════

import json
import logging
from typing import List, Dict, Optional

log = logging.getLogger("MentorMind")


class ConversationManager:
    """
    Conversation history ka manager.
    Save, retrieve, aur context banao.
    """

    SHORT_TERM_LIMIT = 10
    CONTEXT_LIMIT    = 6

    def __init__(self, session_id: str):
        self.session_id = session_id

    def save_user_message(self, message: str):
        """User ka message save karo."""
        try:
            from mentor_mind.database.db_operations import save_message
            save_message(self.session_id, "user", message, "")
        except Exception as e:
            log.error(f"save_user_message error: {e}")

    def save_ai_message(self, message: str, agent_used: str = ""):
        """AI ka response save karo."""
        try:
            from mentor_mind.database.db_operations import save_message
            save_message(self.session_id, "assistant", message, agent_used)
        except Exception as e:
            log.error(f"save_ai_message error: {e}")

    def get_recent_history(self, limit: int = None) -> List[Dict]:
        """Recent messages nikalo."""
        try:
            from mentor_mind.database.db_operations import get_conversation_history
            n = limit or self.SHORT_TERM_LIMIT
            return get_conversation_history(self.session_id, limit=n)
        except Exception as e:
            log.error(f"get_recent_history error: {e}")
            return []

    def build_context_for_ai(self) -> str:
        """AI ke liye context string banao."""
        history = self.get_recent_history(limit=self.CONTEXT_LIMIT)
        if not history:
            return ""
        parts = ["\n--- Previous Conversation ---"]
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            text = msg["message"][:200]
            parts.append(f"{role}: {text}")
        parts.append("--- End ---\n")
        return "\n".join(parts)

    def get_formatted_history(self) -> List[Dict]:
        """Frontend ke liye formatted history."""
        history = self.get_recent_history()
        return [
            {
                "role"     : msg["role"],
                "message"  : msg["message"],
                "agent"    : msg.get("agent_used", ""),
                "timestamp": msg.get("timestamp", "")
            }
            for msg in history
        ]
