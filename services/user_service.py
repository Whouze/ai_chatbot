from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from schemas.user_schema import RegisterUser, ProfileUser, LoginUser, Token
from repository.user_repository import UserRepository
from core.security import get_password_hash, verify_password, create_access_token


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

        # 1. Hash the password using bcrypt
        hashed_password = get_password_hash(user_data.password)
        
        # 2. Save the user to the database
        new_user = self.user_repository.create_user(user_data, hashed_password)
        
        return ProfileUser.model_validate(new_user)

    def login_user(self, user_data: LoginUser, db: Session) -> Token:
        """Login a user by verifying email and password, then returning a JWT token."""
        user = self.user_repository.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 3. Verify the password with bcrypt
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 4. Create the JWT token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # 5. Return the token and profile
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=ProfileUser.model_validate(user)
        )


