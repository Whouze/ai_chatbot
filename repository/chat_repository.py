from uuid import UUID
from sqlalchemy.orm import Session

from models.chat_models import ChatSession, Message
from schemas.chat_schema import ChatSessionCreate, MessageCreate


class ChatRepository:
    """Repository class handling direct database queries for Chat models."""

    def __init__(self, db: Session):
        self.db = db

    # ==========================================
    # CHAT SESSION OPERATIONS
    # ==========================================

    def create_session(self, user_id: UUID, data: ChatSessionCreate) -> ChatSession:
        """Create and persist a new chat session for a user."""
        new_session = ChatSession(
            user_id=user_id,
            title=data.title
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def get_session_by_id(self, session_id: UUID) -> ChatSession | None:
        """Retrieve a single chat session by its ID."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_sessions_by_user(self, user_id: UUID) -> list[ChatSession]:
        """Retrieve all chat sessions belonging to a specific user, ordered by newest first."""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    # ==========================================
    # MESSAGE OPERATIONS
    # ==========================================

    def save_message(self, session_id: UUID, data: MessageCreate) -> Message:
        """Save a single message (user or ai) into the database."""
        new_message = Message(
            session_id=session_id,
            sender=data.sender,
            content=data.content
        )
        self.db.add(new_message)
        self.db.commit()
        self.db.refresh(new_message)
        return new_message

    def get_messages_by_session(self, session_id: UUID) -> list[Message]:
        """Retrieve all messages within a specific chat session, ordered by time."""
        return (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )