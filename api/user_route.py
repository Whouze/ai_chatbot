from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.user_schema import RegisterUser, ProfileUser
from services.user_service import UserService
from repository.user_repository import UserRepository

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=ProfileUser)
async def register_user(
    user_data: RegisterUser, 
    db: Session = Depends(get_db)
):
    """
    Endpoint for registering a new user.
    """
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    new_user = user_service.register_user(user_data, db)
    return new_user

@router.post("/login", response_model=ProfileUser)
async def login_user(
    user_data: RegisterUser, 
    db: Session = Depends(get_db)
):
    """
    Endpoint for logging in a user.
    """
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    logged_user = user_service.login_user(user_data, db)
    return logged_user