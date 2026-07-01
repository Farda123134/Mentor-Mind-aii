
from pydantic import BaseModel, Field
from typing  import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    message    : str = Field(..., min_length=1, max_length=2000)
    session_id : str = Field(default="")
    chat_id    : str = Field(default="")


class ChatResponse(BaseModel):
    response    : str
    session_id  : str
    chat_id     : str       = ""
    agents_used : List[str] = []
    topic       : str       = ""
    intent      : str       = ""
    time_taken  : float     = 0.0
    success     : bool      = True


class HistoryRequest(BaseModel):
    session_id : str = Field(..., description="Session ID")
    limit      : int = Field(default=10, ge=1, le=50)


class HistoryResponse(BaseModel):
    session_id : str
    messages   : List[Dict] = []
    count      : int        = 0


class ProgressRequest(BaseModel):
    session_id : str
    topic      : str


class ProgressResponse(BaseModel):
    topic     : str
    completed : List[str] = []
    pending   : List[str] = []
    percent   : float     = 0.0
    total     : int       = 0


class MarkCompleteRequest(BaseModel):
    session_id : str
    topic      : str
    task       : str


class QuizRequest(BaseModel):
    topic      : str
    count      : int = Field(default=5, ge=1, le=20)
    session_id : str = Field(default="")


class UploadResponse(BaseModel):
    success      : bool
    message      : str
    filename     : str = ""
    chunks_count : int = 0
    doc_id       : str = ""


class NewChatResponse(BaseModel):
    chat_id : str
    title   : str = "New Chat"


class ChatSessionInfo(BaseModel):
    chat_id    : str
    title      : str
    created_at : str
    updated_at : str


class ChatSessionsListResponse(BaseModel):
    sessions : List[ChatSessionInfo] = []
    count    : int = 0


class ChatMessagesResponse(BaseModel):
    chat_id  : str
    title    : str = ""
    messages : List[Dict] = []
    count    : int = 0


class RenameChatRequest(BaseModel):
    chat_id  : str
    new_title: str = Field(..., min_length=1, max_length=200)


class DeleteChatRequest(BaseModel):
    chat_id : str
