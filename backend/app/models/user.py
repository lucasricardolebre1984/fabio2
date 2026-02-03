"""User model."""
from sqlalchemy import Column, String, Boolean, Enum
import enum

from app.db.base import BaseModel


class UserRole(str, enum.Enum):
    """User roles."""
    ADMIN = "admin"
    OPERADOR = "operador"


class User(BaseModel):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.OPERADOR, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
