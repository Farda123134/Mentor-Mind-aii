
# ═══════════════════════════════════════════════════════
# DATABASE OPERATIONS — SQLAlchemy Version
# Purane sqlite3 operations replace kiye SQLAlchemy se
# Ab SQLite aur PostgreSQL dono pe kaam karta hai!
# ═══════════════════════════════════════════════════════

import json
import logging
from datetime import datetime
from typing   import Optional, List, Dict

from sqlalchemy.exc import IntegrityError

from .engine  import get_db_session
from .models  import User, StudyPlan, Progress, Conversation, QuizHistory

log = logging.getLogger("MentorMind")


# ── USER OPERATIONS ───────────────────────────────────

def get_or_create_user(session_id: str, name: str = "Student") -> str:
    """User dhundo ya naya banao."""
    with get_db_session() as db:
        user = db.query(User).filter(
            User.session_id == session_id
        ).first()

        if not user:
            user = User(session_id=session_id, name=name)
            db.add(user)
            log.info(f"New user created: {session_id[:8]}")
        else:
            user.last_active = datetime.utcnow()

    return session_id


# ── STUDY PLAN OPERATIONS ─────────────────────────────

def save_study_plan(session_id: str, topic: str, plan_data: dict):
    """Study plan save ya update karo."""
    # User ensure karo
    get_or_create_user(session_id)

    with get_db_session() as db:
        # Existing plan check karo
        plan = db.query(StudyPlan).filter(
            StudyPlan.session_id == session_id,
            StudyPlan.topic      == topic
        ).first()

        schedule_json = json.dumps(plan_data.get("schedule", []))

        if plan:
            # Update
            plan.schedule   = schedule_json
            plan.total_days = plan_data.get("total_days", 5)
            plan.start_date = plan_data.get("start_date", datetime.now().isoformat())
            log.info(f"Plan updated: {topic}")
        else:
            # Create new
            plan = StudyPlan(
                session_id = session_id,
                topic      = topic,
                total_days = plan_data.get("total_days", 5),
                schedule   = schedule_json,
                start_date = plan_data.get("start_date", datetime.now().isoformat())
            )
            db.add(plan)
            db.flush()  # ID generate karo

            # Progress initialize karo
            pending = [d["task"] for d in plan_data.get("schedule", [])]
            prog    = Progress(
                session_id = session_id,
                topic      = topic,
                plan_id    = plan.id,
                completed  = "[]",
                pending    = json.dumps(pending),
                percent    = 0.0
            )
            db.add(prog)
            log.info(f"Plan created: {topic}")


def get_study_plan(session_id: str, topic: str) -> Optional[dict]:
    """Database se study plan nikalo."""
    with get_db_session() as db:
        plan = db.query(StudyPlan).filter(
            StudyPlan.session_id == session_id,
            StudyPlan.topic      == topic
        ).first()

        if not plan:
            return None

        return {
            "topic"     : plan.topic,
            "total_days": plan.total_days,
            "schedule"  : json.loads(plan.schedule),
            "start_date": plan.start_date
        }


def get_all_plans(session_id: str) -> List[dict]:
    """User ke sare plans nikalo."""
    with get_db_session() as db:
        plans = db.query(StudyPlan).filter(
            StudyPlan.session_id == session_id
        ).all()

        return [
            {
                "topic"     : p.topic,
                "total_days": p.total_days,
                "start_date": p.start_date
            }
            for p in plans
        ]


# ── PROGRESS OPERATIONS ───────────────────────────────

def mark_task_complete(session_id: str, topic: str, task: str):
    """Task complete mark karo."""
    with get_db_session() as db:
        prog = db.query(Progress).filter(
            Progress.session_id == session_id,
            Progress.topic      == topic
        ).first()

        if prog:
            completed = json.loads(prog.completed)
            pending   = json.loads(prog.pending)

            if task in pending:
                pending.remove(task)
                completed.append(task)

                total           = len(completed) + len(pending)
                prog.completed  = json.dumps(completed)
                prog.pending    = json.dumps(pending)
                prog.percent    = round(len(completed) / total * 100, 1) if total else 0
                prog.updated_at = datetime.utcnow()
                log.info(f"Task completed: {task[:40]}")


def get_progress(session_id: str, topic: str) -> dict:
    """Progress summary nikalo."""
    with get_db_session() as db:
        prog = db.query(Progress).filter(
            Progress.session_id == session_id,
            Progress.topic      == topic
        ).first()

        if not prog:
            return {}

        completed = json.loads(prog.completed)
        pending   = json.loads(prog.pending)
        total     = len(completed) + len(pending)

        return {
            "completed": completed,
            "pending"  : pending,
            "percent"  : prog.percent,
            "total"    : total
        }


# ── CONVERSATION OPERATIONS ───────────────────────────

def save_message(
    session_id : str,
    role       : str,
    message    : str,
    agent_used : str = ""
):
    """Message save karo."""
    get_or_create_user(session_id)

    with get_db_session() as db:
        conv = Conversation(
            session_id = session_id,
            role       = role,
            message    = message[:5000],  # Limit length
            agent_used = agent_used,
            timestamp  = datetime.utcnow()
        )
        db.add(conv)


def get_conversation_history(
    session_id : str,
    limit      : int = 10
) -> List[dict]:
    """Recent messages nikalo."""
    with get_db_session() as db:
        convs = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(
            Conversation.timestamp.desc()
        ).limit(limit).all()

        # Reverse karo — purani baat pehle
        return [
            {
                "role"      : c.role,
                "message"   : c.message,
                "agent_used": c.agent_used,
                "timestamp" : c.timestamp.isoformat() if c.timestamp else ""
            }
            for c in reversed(convs)
        ]


# ── QUIZ OPERATIONS ───────────────────────────────────

def save_quiz_result(
    session_id : str,
    topic      : str,
    score      : int,
    total      : int,
    questions  : list,
    answers    : dict
):
    """Quiz result save karo."""
    get_or_create_user(session_id)

    with get_db_session() as db:
        quiz = QuizHistory(
            session_id = session_id,
            topic      = topic,
            score      = score,
            total      = total,
            percentage = round(score / total * 100, 1) if total else 0,
            questions  = json.dumps(questions),
            answers    = json.dumps(answers),
            taken_at   = datetime.utcnow()
        )
        db.add(quiz)
        log.info(f"Quiz saved: {topic} — {score}/{total}")


def get_quiz_history(
    session_id : str,
    topic      : str = None
) -> List[dict]:
    """Quiz history nikalo."""
    with get_db_session() as db:
        query = db.query(QuizHistory).filter(
            QuizHistory.session_id == session_id
        )
        if topic:
            query = query.filter(QuizHistory.topic == topic)

        results = query.order_by(
            QuizHistory.taken_at.desc()
        ).limit(20).all()

        return [
            {
                "topic"     : r.topic,
                "score"     : r.score,
                "total"     : r.total,
                "percentage": r.percentage,
                "taken_at"  : r.taken_at.isoformat() if r.taken_at else ""
            }
            for r in results
        ]




# ── CHAT SESSION OPERATIONS ───────────────────────────

def create_chat_session(session_id: str, title: str = "New Chat") -> str:
    """
    Naya chat session banao, chat_id return karo.
    SAFETY: pehle ensure karo ke "users" table mein
    session_id exist karta hai — warna Foreign Key fail hoga.
    """
    import uuid
    from mentor_mind.database.models import ChatSession, User
    from mentor_mind.database.engine import get_db_session

    chat_id = "chat_" + uuid.uuid4().hex[:16]

    with get_db_session() as db:
        # Pehle users table check karo
        base_user = db.query(User).filter(User.session_id == session_id).first()
        if not base_user:
            base_user = User(session_id=session_id, name="Student")
            db.add(base_user)
            db.flush()
            log.info("Auto-created users entry for session: " + session_id[:20])

        cs = ChatSession(chat_id=chat_id, session_id=session_id, title=title)
        db.add(cs)

    log.info("Chat session created: " + chat_id)
    return chat_id


def get_chat_sessions(session_id: str) -> list:
    """User ke sare chat sessions nikalo (latest first)."""
    from mentor_mind.database.models import ChatSession
    from mentor_mind.database.engine import get_db_session

    with get_db_session() as db:
        sessions = db.query(ChatSession).filter(
            ChatSession.session_id == session_id,
            ChatSession.is_deleted == False
        ).order_by(ChatSession.updated_at.desc()).all()

        return [
            {
                "chat_id"   : s.chat_id,
                "title"     : s.title,
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "updated_at": s.updated_at.isoformat() if s.updated_at else ""
            }
            for s in sessions
        ]


def get_chat_messages(session_id: str, chat_id: str) -> list:
    """Ek specific chat session ke sare messages nikalo."""
    from mentor_mind.database.models import Conversation
    from mentor_mind.database.engine import get_db_session

    with get_db_session() as db:
        msgs = db.query(Conversation).filter(
            Conversation.session_id == session_id,
            Conversation.chat_id    == chat_id
        ).order_by(Conversation.timestamp.asc()).all()

        return [
            {
                "role"      : m.role,
                "message"   : m.message,
                "agent_used": m.agent_used,
                "timestamp" : m.timestamp.isoformat() if m.timestamp else ""
            }
            for m in msgs
        ]


def save_message_to_chat(session_id: str, chat_id: str, role: str, message: str, agent_used: str = ""):
    """Message ko specific chat session mein save karo. FK-safe."""
    from mentor_mind.database.models import Conversation, ChatSession, User
    from mentor_mind.database.engine import get_db_session
    from datetime import datetime

    with get_db_session() as db:
        # FK safety
        base_user = db.query(User).filter(User.session_id == session_id).first()
        if not base_user:
            base_user = User(session_id=session_id, name="Student")
            db.add(base_user)
            db.flush()

        conv = Conversation(
            session_id = session_id,
            chat_id    = chat_id,
            role       = role,
            message    = message[:5000],
            agent_used = agent_used,
            timestamp  = datetime.utcnow()
        )
        db.add(conv)

        cs = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
        if cs:
            cs.updated_at = datetime.utcnow()


def auto_title_from_message(message: str) -> str:
    """Pehle message se title generate karo."""
    title = message.strip()[:50]
    if len(message) > 50:
        title += "..."
    return title or "New Chat"


def rename_chat_session(session_id: str, chat_id: str, new_title: str) -> bool:
    """Chat session ka title change karo."""
    from mentor_mind.database.models import ChatSession
    from mentor_mind.database.engine import get_db_session

    with get_db_session() as db:
        cs = db.query(ChatSession).filter(
            ChatSession.chat_id    == chat_id,
            ChatSession.session_id == session_id
        ).first()
        if not cs:
            return False
        cs.title = new_title[:200]
        return True


def delete_chat_session(session_id: str, chat_id: str) -> bool:
    """Chat session soft-delete karo."""
    from mentor_mind.database.models import ChatSession
    from mentor_mind.database.engine import get_db_session

    with get_db_session() as db:
        cs = db.query(ChatSession).filter(
            ChatSession.chat_id    == chat_id,
            ChatSession.session_id == session_id
        ).first()
        if not cs:
            return False
        cs.is_deleted = True
        return True
