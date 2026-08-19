from fastapi import FastAPI
from core.database import engine, Base

from models.user_models import UserModels
from api.user_route import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chatbot API")
app.include_router(user_router)

@app.get("/")
def ping_server():
    return {"status": "success", "message": "Server and Database are running!"}
