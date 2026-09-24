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

# Router untuk REST API (history)
router = APIRouter(prefix="/chat", tags=["Chat History"])

# Router untuk WebSocket (real-time chat)
ws_router = APIRouter(prefix="/ws", tags=["WebSocket Chat"])

gemini_service = GeminiService()


# ==========================================
# REST API — CHAT HISTORY ENDPOINTS
# ==========================================

@router.get("/sessions/{user_id}", response_model=list[ChatSessionListResponse])
def get_user_sessions(user_id: UUID, db: Session = Depends(get_db)):
    """Retrieve all chat sessions belonging to a specific user."""
    chat_repo = ChatRepository(db)
    sessions = chat_repo.get_sessions_by_user(user_id=user_id)
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chat sessions found for this user."
        )
    return sessions


@router.get("/history/{session_id}", response_model=list[MessageResponse])
def get_session_history(session_id: UUID, db: Session = Depends(get_db)):
    """Retrieve all messages within a specific chat session."""
    chat_repo = ChatRepository(db)

    session = chat_repo.get_session_by_id(session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found."
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
            # 1. Terima payload JSON dari Frontend
            raw_data = await websocket.receive_json()

            # 2. Validasi payload menggunakan Pydantic Schema
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

            # 3. Ambil atau buat sesi baru jika session_id tidak dikirim
            session_id: UUID = payload.session_id
            if not session_id:
                new_session = chat_repo.create_session(
                    user_id=UUID(user_id),
                    data=ChatSessionCreate(title=payload.message[:50])
                )
                session_id = new_session.id
                logger.info(f"New chat session created: session_id='{session_id}'")

            # 4. Simpan pesan user ke database
            chat_repo.save_message(
                session_id=session_id,
                data=MessageCreate(sender="user", content=payload.message)
            )

            # 5. Stream balasan Gemini + RAG per chunk kata ke WebSocket
            full_ai_response = ""
            for chunk_text in gemini_service.Handling_GeminiStreamResponse(
                user_id=user_id,
                user_input=payload.message,
                file_paths=payload.file_paths
            ):
                full_ai_response += chunk_text
                stream_res = WebSocketStreamChunk(content=chunk_text)
                await manager.send_json(stream_res.model_dump(), websocket)

            # 6. Simpan balasan AI ke database setelah streaming selesai
            chat_repo.save_message(
                session_id=session_id,
                data=MessageCreate(sender="ai", content=full_ai_response)
            )
            logger.info(f"AI response saved to database for session '{session_id}'")

            # 7. Kirim sinyal bahwa streaming selesai beserta session_id
            done_res = WebSocketDoneResponse(session_id=session_id)
            await manager.send_json(done_res.model_dump(mode="json"), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected: user_id='{user_id}'")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint for user '{user_id}': {e}")
        manager.disconnect(websocket)
