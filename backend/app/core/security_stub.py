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
