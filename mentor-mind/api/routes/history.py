
import logging
import traceback

from fastapi           import APIRouter, HTTPException, Depends
from fastapi.security  import HTTPBearer, HTTPAuthorizationCredentials

from mentor_mind.api.models.schemas import (
    NewChatResponse, ChatSessionsListResponse,
    ChatMessagesResponse, RenameChatRequest, DeleteChatRequest
)
from mentor_mind.auth.auth_service import get_current_user

log      = logging.getLogger("MentorMind")
router   = APIRouter(prefix="/history", tags=["Chat History"])
security = HTTPBearer()


def get_session_id_from_token(credentials: HTTPAuthorizationCredentials) -> str:
    user = get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user["session_id"]


@router.post("/new", response_model=NewChatResponse)
async def new_chat(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Naya chat session shuru karo."""
    try:
        session_id = get_session_id_from_token(credentials)
        from mentor_mind.database.db_operations import create_chat_session
        chat_id = create_chat_session(session_id, "New Chat")
        return NewChatResponse(chat_id=chat_id, title="New Chat")
    except HTTPException:
        raise
    except Exception as e:
        log.error("new_chat error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not create new chat")


@router.get("/list", response_model=ChatSessionsListResponse)
async def list_chats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User ke sare chat sessions ki list — latest first."""
    try:
        session_id = get_session_id_from_token(credentials)
        from mentor_mind.database.db_operations import get_chat_sessions
        sessions = get_chat_sessions(session_id)
        return ChatSessionsListResponse(sessions=sessions, count=len(sessions))
    except HTTPException:
        raise
    except Exception as e:
        log.error("list_chats error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not load chat list")


@router.get("/{chat_id}/messages", response_model=ChatMessagesResponse)
async def get_chat_messages_route(
    chat_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Ek specific chat ki sari messages load karo."""
    try:
        session_id = get_session_id_from_token(credentials)
        from mentor_mind.database.db_operations import get_chat_messages, get_chat_sessions

        messages = get_chat_messages(session_id, chat_id)

        title = ""
        for s in get_chat_sessions(session_id):
            if s["chat_id"] == chat_id:
                title = s["title"]
                break

        return ChatMessagesResponse(
            chat_id  = chat_id,
            title    = title,
            messages = messages,
            count    = len(messages)
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error("get_chat_messages error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not load messages")


@router.post("/rename")
async def rename_chat(
    request: RenameChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Chat session ka title change karo."""
    try:
        session_id = get_session_id_from_token(credentials)
        from mentor_mind.database.db_operations import rename_chat_session
        success = rename_chat_session(session_id, request.chat_id, request.new_title)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"success": True, "message": "Renamed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error("rename_chat error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not rename chat")


@router.post("/delete")
async def delete_chat(
    request: DeleteChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Chat session delete karo (soft delete)."""
    try:
        session_id = get_session_id_from_token(credentials)
        from mentor_mind.database.db_operations import delete_chat_session
        success = delete_chat_session(session_id, request.chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        return {"success": True, "message": "Deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        log.error("delete_chat error: " + str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Could not delete chat")
