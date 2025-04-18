from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database.db import Base


class BookStatus(str, enum.Enum):
    """Enum for book status."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Book(Base):
    """
    Book model for storing book creation requests and their status.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_name = Column(String, nullable=False)
    adventure_type = Column(String, nullable=False)
    status = Column(String, default=BookStatus.PROCESSING)
    
    # S3 storage fields
    photos_s3_keys = Column(JSON, nullable=True)  # List of S3 keys for uploaded photos
    pdf_s3_key = Column(String, nullable=True)    # S3 key for the generated PDF
    thumbnail_s3_key = Column(String, nullable=True)  # S3 key for the book thumbnail
    
    download_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationship with User
    user = relationship("User", back_populates="books") 