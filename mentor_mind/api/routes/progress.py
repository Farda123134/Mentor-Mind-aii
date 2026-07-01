
# ═══════════════════════════════════════════════════════
# PROGRESS ROUTES
# Study progress related endpoints
# ═══════════════════════════════════════════════════════

import logging
from fastapi  import APIRouter, HTTPException
from ..models.schemas import (
    ProgressRequest, ProgressResponse,
    MarkCompleteRequest
)

log    = logging.getLogger("MentorMind")
router = APIRouter(
    prefix = "/progress",
    tags   = ["Progress"]
)


# ── POST /progress ────────────────────────────────────
@router.post(
    "/",
    response_model = ProgressResponse,
    summary        = "Get study progress",
    description    = "Topic ki progress check karo."
)
async def get_progress(request: ProgressRequest):
    """Study progress nikalo."""
    try:
        from mentor_mind.database.db_operations import get_progress

        data = get_progress(request.session_id, request.topic)

        if not data:
            return ProgressResponse(
                topic   = request.topic,
                percent = 0.0,
                total   = 0
            )

        return ProgressResponse(
            topic     = request.topic,
            completed = data.get("completed", []),
            pending   = data.get("pending", []),
            percent   = data.get("percent", 0.0),
            total     = data.get("total", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── POST /progress/mark-complete ──────────────────────
@router.post(
    "/mark-complete",
    summary     = "Mark task as complete",
    description = "Ek task complete mark karo."
)
async def mark_complete(request: MarkCompleteRequest):
    """Task ko complete mark karo."""
    try:
        from mentor_mind.database.db_operations import mark_task_complete

        mark_task_complete(
            request.session_id,
            request.topic,
            request.task
        )

        return {
            "success" : True,
            "message" : f"Task marked complete: {request.task}",
            "topic"   : request.topic
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── GET /progress/plans ───────────────────────────────
@router.get(
    "/plans/{session_id}",
    summary     = "Get all study plans",
    description = "User ke sare plans nikalo."
)
async def get_plans(session_id: str):
    """Sare study plans nikalo."""
    try:
        from mentor_mind.database.db_operations import get_all_plans

        plans = get_all_plans(session_id)
        return {
            "session_id": session_id,
            "plans"     : plans,
            "count"     : len(plans)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
