from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AdventureType(str, Enum):
    """Adventure types available for books."""
    FANTASY = "fantasy"
    SUPERHERO = "superhero"
    SPACE = "space"
    UNDERWATER = "underwater"
    FAIRY_TALE = "fairy_tale"
    JUNGLE = "jungle"


class BookStatus(str, Enum):
    """Book creation status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BookCreate(BaseModel):
    """Schema for book creation request."""
    child_name: str = Field(..., min_length=1, max_length=100)
    adventure_type: AdventureType
    email: EmailStr


class BookResponse(BaseModel):
    """Schema for book response."""
    id: int
    child_name: str
    adventure_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class BookListResponse(BaseModel):
    """Schema for paginated book list response."""
    total: int
    page: int
    limit: int
    books: List[BookResponse]
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True 