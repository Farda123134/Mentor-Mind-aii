import uuid
import time
import logging
import traceback

from fastapi           import APIRouter, HTTPException, Depends
from fastapi.security  import HTTPBearer, HTTPAuthorizationCredentials

from mentor_mind.api.models.schemas import ChatRequest, ChatResponse, HistoryRequest, HistoryResponse
from mentor_mind.auth.auth_service  import get_current_user

log      = logging.getLogger("MentorMind")
router   = APIRouter(prefix="/chat", tags=["Chat"])
security = HTTPBearer(auto_error=False)


def get_coordinator():
    from mentor_mind.api.main import coordinator
    return coordinator


@router.post("/", response_model=ChatResponse)
async def chat(
    request     : ChatRequest,
    credentials : HTTPAuthorizationCredentials = Depends(security),
    coordinator = Depends(get_coordinator)
):
    start_time = time.time()
    session_id = request.session_id or str(uuid.uuid4())

    if credentials:
        try:
            user = get_current_user(credentials.credentials)
            if user:
                session_id = user["session_id"]
        except Exception as e:
            log.error("Token verification crashed: " + str(e))
            traceback.print_exc()

    log.info("Chat session=" + session_id[:8] + " msg=" + request.message[:50])

    chat_id = request.chat_id

    # ── STEP 1: chat session create karo ──────────────
    try:
        from mentor_mind.database.db_operations import create_chat_session, auto_title_from_message, rename_chat_session
        is_new_chat = False
        if not chat_id:
            chat_id = create_chat_session(session_id, "New Chat")
            is_new_chat = True
    except Exception as e:
        log.error("STEP 1 (create_chat_session) FAILED: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error: could not create chat session")

    # ── STEP 2: user message save karo ────────────────
    try:
        from mentor_mind.database.db_operations import save_message_to_chat
        save_message_to_chat(session_id, chat_id, "user", request.message)
        if is_new_chat:
            title = auto_title_from_message(request.message)
            rename_chat_session(session_id, chat_id, title)
    except Exception as e:
        log.error("STEP 2 (save_message_to_chat) FAILED: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Database error: could not save message")

    # ── STEP 3: agent se response lo ──────────────────
    try:
        result = coordinator.handle(request.message, session_id=session_id)
    except Exception as e:
        log.error("STEP 3 (coordinator.handle) FAILED: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Agent error: " + str(e))

    # ── STEP 4: response build karo ────────────────────
    try:
        response_text = result.get("final_response") or ""
        if not response_text:
            from mentor_mind.api.main import build_response
            response_text = build_response(result)

        agents_used = result.get("agents_used", [])
        route       = result.get("route", {}) or {}
        safe_topic  = route.get("topic") or ""
        safe_intent = route.get("intent") or ""
    except Exception as e:
        log.error("STEP 4 (build response) FAILED: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Response build error: " + str(e))

    # ── STEP 5: AI response save karo ──────────────────
    try:
        save_message_to_chat(session_id, chat_id, "assistant", response_text, ", ".join(agents_used))
    except Exception as e:
        log.error("STEP 5 (save AI message) FAILED: " + str(e))
        traceback.print_exc()
        # Yeh fail ho to bhi response user ko do — message save nahi hui, but answer mil gaya

    return ChatResponse(
        response    = response_text,
        session_id  = session_id,
        chat_id     = chat_id,
        agents_used = agents_used,
        topic       = safe_topic,
        intent      = safe_intent,
        time_taken  = round(time.time() - start_time, 2),
        success     = True
    )


@router.post("/history", response_model=HistoryResponse)
async def get_history(
    request     : HistoryRequest,
    credentials : HTTPAuthorizationCredentials = Depends(security)
):
    session_id = request.session_id
    if credentials:
        try:
            user = get_current_user(credentials.credentials)
            if user:
                session_id = user["session_id"]
        except Exception:
            pass
    try:
        from mentor_mind.memory.conversation_manager import ConversationManager
        conv     = ConversationManager(session_id)
        messages = conv.get_formatted_history()
        return HistoryResponse(session_id=session_id, messages=messages[:request.limit], count=len(messages))
    except Exception as e:
        log.error("History error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not load history")


@router.get("/new-session")
async def new_session():
    return {"session_id": str(uuid.uuid4()), "message": "New session created!"}
