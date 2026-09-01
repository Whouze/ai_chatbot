from pydantic import BaseModel, Field
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
