from fastapi import FastAPI
from core.database import engine, Base

from models.user_models import UserModels
from models.chat_models import ChatSession, Message
from api.user_route import router as user_router
from api.chat_route import router as chat_router, ws_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chatbot API")
app.include_router(user_router)
app.include_router(chat_router)   # REST: GET /chat/sessions, GET /chat/history
app.include_router(ws_router)     # WebSocket: ws://…/ws/chat/{user_id}


@app.get("/")
def ping_server():
    return {"status": "success", "message": "Server and Database are running!"}

