from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from utils.websocket_manager import manager
from utils.logger import logger
from services.gemini_service import GeminiService
from schemas.chat_schema import (
    WebSocketChatRequest,
    WebSocketStreamChunk,
    WebSocketDoneResponse,
    WebSocketErrorResponse
)

router = APIRouter(prefix="/ws", tags=["WebSocket Chat"])
gemini_service = GeminiService()


@router.websocket("/chat/{user_id}")
async def chat_websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time streaming chat with RAG and Gemini.
    Validates incoming JSON payload against WebSocketChatRequest schema.
    """
    await manager.connect(websocket)
    logger.info(f"WebSocket client connected: user_id='{user_id}'")

    try:
        while True:
            # 1. Menerima payload JSON dari Frontend
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

            logger.info(f"Received valid message from user '{user_id}': {payload.message[:30]}...")

            # 3. Stream balasan Gemini + RAG kata demi kata
            for chunk_text in gemini_service.Handling_GeminiStreamResponse(
                user_id=user_id,
                user_input=payload.message,
                file_paths=payload.file_paths
            ):
                stream_res = WebSocketStreamChunk(content=chunk_text)
                await manager.send_json(stream_res.model_dump(), websocket)

            # 4. Sinyal bahwa streaming selesai
            done_res = WebSocketDoneResponse(session_id=payload.session_id)
            await manager.send_json(done_res.model_dump(mode="json"), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket client disconnected: user_id='{user_id}'")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket endpoint for user '{user_id}': {e}")
        manager.disconnect(websocket)
