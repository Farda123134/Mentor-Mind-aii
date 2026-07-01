
from mentor_mind.database.db_setup      import create_tables, check_database
from mentor_mind.database.db_operations import (
    get_or_create_user,
    save_study_plan,
    get_study_plan,
    get_all_plans,
    mark_task_complete,
    get_progress,
    save_message,
    get_conversation_history,
    save_quiz_result,
    get_quiz_history,
)
from mentor_mind.database.engine import get_db, get_db_session
from mentor_mind.database.models import (
    User, StudyPlan, Progress,
    Conversation, QuizHistory
)

__all__ = [
    "create_tables", "check_database",
    "get_or_create_user",
    "save_study_plan", "get_study_plan", "get_all_plans",
    "mark_task_complete", "get_progress",
    "save_message", "get_conversation_history",
    "save_quiz_result", "get_quiz_history",
    "get_db", "get_db_session",
    "User", "StudyPlan", "Progress",
    "Conversation", "QuizHistory",
]
