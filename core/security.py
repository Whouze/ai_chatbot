from datetime import datetime, timedelta
import bcrypt
import jwt

from utils.config import settings

# 1. Fungsi Hashing Password (menggunakan bcrypt langsung)
def get_password_hash(password: str) -> str:
    """Mengenkripsi password mentah menjadi hash bcrypt."""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi apakah password mentah cocok dengan hash di database."""
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=plain_password_bytes, hashed_password=hashed_password_bytes)

# 3. Fungsi Pembuatan Token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Membuat JWT token dengan data payload dan waktu kadaluarsa."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    # Generate token string menggunakan secret key
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt
