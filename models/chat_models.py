import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UUID
from sqlalchemy.orm import relationship
from core.database import Base


class ChatSession(Base):
    """Represents a single conversation session between a user and the AI."""
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False, default="Sesi Baru")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: 1 sesi bisa punya banyak pesan
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    """Represents a single chat message (user or AI) within a session."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(String(10), nullable=False)  # "user" or "ai"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship: setiap pesan terhubung ke 1 sesi
    session = relationship("ChatSession", back_populates="messages")