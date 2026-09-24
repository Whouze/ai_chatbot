from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

# ==========================================
# WEBSOCKET SCHEMAS (Request & Response DTOs)
# ==========================================

class WebSocketChatRequest(BaseModel):
    """Schema for incoming WebSocket JSON payload from Client."""
    message: str = Field(..., min_length=1, description="User text message")
    session_id: UUID | None = Field(default=None, description="Optional chat session UUID")
    file_paths: list[str] | None = Field(default=None, description="Optional list of uploaded file paths")


class WebSocketStreamChunk(BaseModel):
    """Schema for streaming chunk response sent to Client."""
    type: str = "stream"
    content: str


class WebSocketDoneResponse(BaseModel):
    """Schema for stream completion signal sent to Client."""
    type: str = "done"
    session_id: UUID | None = None


class WebSocketErrorResponse(BaseModel):
    """Schema for error messages sent to Client."""
    type: str = "error"
    content: str


# ==========================================
# CHAT DATABASE SCHEMAS (Request & Response DTOs)
# ==========================================

class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    title: str = "Sesi Baru"


class MessageCreate(BaseModel):
    """Schema for saving a new message into the database."""
    sender: str = Field(..., pattern="^(user|ai)$", description="Message sender: 'user' or 'ai'")
    content: str = Field(..., min_length=1, description="Message content")


class MessageResponse(BaseModel):
    """Schema for a single message returned to the Client."""
    id: UUID
    session_id: UUID
    sender: str  # "user" or "ai"
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionListResponse(BaseModel):
    """Schema for session list — returns session info only (no messages)."""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionResponse(BaseModel):
    """Schema for a full chat session including all its messages."""
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    messages: list[MessageResponse] = []

    model_config = ConfigDict(from_attributes=True)

