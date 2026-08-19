from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import hashlib

from schemas.user_schema import RegisterUser, ProfileUser
from repository.user_repository import UserRepository


class UserService:
    """Business logic service layer for User management."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_user(self, user_data: RegisterUser, db: Session) -> ProfileUser:
        """Register a new user after verifying email uniqueness and hashing password."""
        if self.user_repository.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        new_user = self.user_repository.create_user(user_data, hashed_password)
        
        return ProfileUser.model_validate(new_user)

    def login_user(self, user_data: RegisterUser, db: Session) -> ProfileUser:
        """Login a user by verifying email and password."""
        user = self.user_repository.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
        if user.password != hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        return ProfileUser.model_validate(user)


