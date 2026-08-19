from sqlalchemy.orm import Session
from models.user_models import UserModels
from schemas.user_schema import RegisterUser

class UserRepository:
    """Repository class handling direct database queries for User models."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: RegisterUser, hashed_password: str) -> UserModels:
        """Create and persist a new user record in the database."""
        new_user = UserModels(
            username=user.username,
            email=user.email,
            password=hashed_password
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user_by_email(self, email: str) -> UserModels | None:
        """Retrieve a user by their email address."""
        return self.db.query(UserModels).filter(UserModels.email == email).first()

    def get_user_by_id(self, user_id) -> UserModels | None:
        """Retrieve a user by their unique ID."""
        return self.db.query(UserModels).filter(UserModels.id == user_id).first()
