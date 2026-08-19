import uuid  # Built-in Python module for generating UUID values (e.g. uuid4)
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UUID
from datetime import datetime
from core.database import Base

class UserModels(Base):
    __tablename__ = "users"  # Database table name

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)  # Primary key column (UUID)
    username = Column(String(50), unique=True, nullable=False)  # Username column
    email = Column(String(100), unique=True, nullable=False)  # Email column
    password = Column(String(255), nullable=False)  # Hashed password column
    created_at = Column(DateTime, default=datetime.utcnow)  # Creation timestamp column