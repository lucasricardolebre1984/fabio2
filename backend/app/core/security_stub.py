"""
STUB temporário para security - bcrypt com problemas no Windows
Usar apenas para desenvolvimento local!
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings

# Stub simples para desenvolvimento
# Em produção, usar bcrypt real

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - DEV MODE: comparação direta para teste"""
    # SECURITY: Stub only works in development/staging
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            "security_stub.py must not be used in production! "
            "Use the real security.py module with bcrypt."
        )
    
    # MODO DESENVOLVIMENTO: aceita senha "1234" para qualquer hash
    # ou comparação direta se o hash for o nosso conhecido
    DEV_PASSWORD = "1234"
    KNOWN_HASH = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    
    if plain_password == DEV_PASSWORD:
        return True
    if hashed_password == KNOWN_HASH and plain_password == DEV_PASSWORD:
        return True
    return False

def get_password_hash(password: str) -> str:
    """Hash password - DEV MODE: retorna hash fixo"""
    # Retorna hash pré-computado de "1234"
    return "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_token_pair(user_id: str):
    """Create both access and refresh tokens."""
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    expires_in = 900  # 15 minutes in seconds
    return access_token, refresh_token, expires_in


def decode_token(token: str):
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
