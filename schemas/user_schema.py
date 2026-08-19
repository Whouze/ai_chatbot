from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from uuid import UUID
from datetime import datetime

# Custom password validator
def validate_password(cls, password: str) -> str:
    if not any(char.isupper() for char in password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not any(char.islower() for char in password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not any(char.isdigit() for char in password):
        raise ValueError('Password must contain at least one digit')
    return password

# 1. BASE SCHEMA (Stores common fields shared across schemas)
class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr

# 2. REGISTER SCHEMA (Inherits UserBase and adds password field)
class RegisterUser(UserBase):
    password: str = Field(min_length=8, max_length=32)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        return validate_password(cls, password)

# 3. LOGIN SCHEMA (Standalone schema for user authentication)
class LoginUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=32)

# 4. UPDATE SCHEMA (Inherits UserBase with optional fields for profile updates)
class UpdateUser(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=50)
    email: EmailStr | None = Field(None)
    password: str | None = Field(None, min_length=8, max_length=32)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if password is not None:
            return validate_password(cls, password)
        return password

# 5. RESPONSE / PROFILE SCHEMA (Inherits UserBase and adds id and creation timestamp)
class ProfileUser(UserBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
