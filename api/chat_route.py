from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from core.database import get_db
from utils.websocket_manager import manager
from utils.logger import logger
from services.gemini_service import GeminiService
from repository.chat_repository import ChatRepository
from schemas.chat_schema import (
    ChatSessionCreate,
    MessageCreate,
    ChatSessionListResponse,
    ChatSessionResponse,
    MessageResponse,
    WebSocketChatRequest,
    WebSocketStreamChunk,
    WebSocketDoneResponse,
    WebSocketErrorResponse
)

# Router for REST API history endpoints
router = APIRouter(prefix="/chat", tags=["Chat History"])

# Router for real-time WebSocket chat
ws_router = APIRouter(prefix="/ws", tags=["WebSocket Chat"])

gemini_service = GeminiService()


from core.security import get_current_user
from models.user_models import UserModels

# ==========================================
# REST API — CHAT HISTORY ENDPOINTS
# ==========================================

@router.get("/sessions", response_model=list[ChatSessionListResponse])
def get_user_sessions(
    current_user: UserModels = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Retrieve all chat sessions belonging to the currently logged-in user."""
    chat_repo = ChatRepository(db)
    # Kita tidak butuh user_id dari URL lagi, karena otomatis diambil dari token!
    sessions = chat_repo.get_sessions_by_user(user_id=current_user.id)
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chat sessions found for this user."
        )
    return sessions


@router.get("/history/{session_id}", response_model=list[MessageResponse])
def get_session_history(
    session_id: UUID, 
    current_user: UserModels = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Retrieve all messages within a specific chat session securely."""
    chat_repo = ChatRepository(db)

    session = chat_repo.get_session_by_id(session_id=session_id)
    # Proteksi: Pastikan sesi ini benar-benar milik user yang sedang login!
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found or access denied."
        )

    messages = chat_repo.get_messages_by_session(session_id=session_id)
    return messages




@ws_router.websocket("/chat/{user_id}")
async def chat_websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time streaming chat with RAG and Gemini.
    Validates incoming JSON payload, streams Gemini response, and saves to database.
    """
    await manager.connect(websocket)
    logger.info(f"WebSocket client connected: user_id='{user_id}'")
    chat_repo = ChatRepository(db)

    try:
        while True:
            # 1. Receive JSON payload from the frontend
            raw_data = await websocket.receive_json()

            # 2. Validate payload using the Pydantic schema
            try:
                payload = WebSocketChatRequest.model_validate(raw_data)
            except ValidationError as err:
                logger.warning(f"Invalid WebSocket payload from user '{user_id}': {err.errors()}")
                error_res = WebSocketErrorResponse(
                    content=f"Invalid payload format: {err.errors()[0]['msg']}"
                )
                await manager.send_json(error_res.model_dump(), websocket)
                continue

            logger.info(f"Received message from user '{user_id}': {payload.message[:50]}...")

            # 3. Fetch or create a new session when session_id is not provided
            session_id: UUID = payload.session_id
            if not session_id:
                new_session = chat_repo.create_session(
                    user_id=UUID(user_id),
                    data=ChatSessionCreate(title=payload.message[:50])
                )
                session_id = new_session.id
                logger.info(f"New chat session created: session_id='{session_id}'")

            # 4. Save the user message to the database
            chat_repo.save_message(
                session_id=session_id,
                data=MessageCreate(sender="user", content=payload.message)
            )

            # 5. Stream Gemini + RAG response chunks to the WebSocket
            full_ai_response = ""
            for chunk_text in gemini_service.Handling_GeminiStreamResponse(
                user_id=user_id,
                user_input=payload.message,
                file_paths=payload.file_paths
            ):
                full_ai_response += chunk_text
                stream_res = WebSocketStreamChunk(content=chunk_text)
                await manager.send_json(stream_res.model_dump(), websocket)

            # 6. Save the AI response to the database after streaming completes
            chat_repo.save_message(
                session_id=session_id,
                data=MessageCreate(sender="ai", content=full_ai_response)
            )
            logger.info(f"AI response saved to database for session '{session_id}'")

            # 7. Send the completion signal with the session_id
            done_res = WebSocketDoneResponse(session_id=session_id)
            await manager.send_json(done_res.model_dump(mode="json"), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected: user_id='{user_id}'")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint for user '{user_id}': {e}")
        manager.disconnect(websocket)
