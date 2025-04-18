from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8)
    name: Optional[str] = None


class UserLogin(UserBase):
    """Schema for user login."""
    password: str


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = None 