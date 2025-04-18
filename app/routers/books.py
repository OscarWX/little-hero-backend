from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query, Response
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Any
from datetime import datetime
import os
import uuid
import json

from app.database.db import get_db
from app.models.book import Book, BookStatus
from app.models.user import User
from app.schemas.book import BookCreate, BookResponse, BookListResponse, AdventureType
from app.utils.auth import get_current_user
from app.utils.storage import upload_files_to_s3, generate_presigned_url

# Create a router for book-related operations
router = APIRouter(prefix="/api/books", tags=["books"])

# Mock function for book generation (in a real app, this would call OpenAI, DALL-E, etc.)
async def generate_book_mock(book_id: int, child_name: str, adventure_type: str, photos_s3_keys: List[str]) -> None:
    """
    Mock function to simulate book generation.
    In a real implementation, this would call external APIs for story and image generation.
    
    Args:
        book_id: The ID of the book
        child_name: The name of the child
        adventure_type: The type of adventure
        photos_s3_keys: List of S3 keys for uploaded photos
    """
    # In a real app, this would be an async task that:
    # 1. Calls OpenAI/GPT to generate a story
    # 2. Calls DALL-E to generate illustrations
    # 3. Compiles the book into a PDF and uploads to S3
    # 4. Updates the book status in the database
    
    # For this example, we'll just simulate the process with logs
    print(f"Generating book {book_id} for {child_name} with adventure type {adventure_type}")
    print(f"Using photos from S3 keys: {photos_s3_keys}")
    # In a real app, this would be handled by a background task/worker


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    child_name: str = Form(...),
    adventure_type: AdventureType = Form(...),
    photos: List[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new book request.
    
    Args:
        child_name: The name of the child
        adventure_type: The type of adventure
        photos: List of uploaded photos
        user: The current authenticated user
        db: The database session
        
    Returns:
        BookResponse: The created book
    """
    # Define allowed photo types
    allowed_photo_types = ["image/jpeg", "image/png", "image/jpg"]
    
    # Define maximum file size (5 MB)
    max_photo_size_mb = 5
    
    # Create a book record
    book = Book(
        user_id=user.id,
        child_name=child_name,
        adventure_type=adventure_type.value,
        status=BookStatus.PROCESSING
    )
    
    # Add book to database to get an ID
    db.add(book)
    await db.commit()
    await db.refresh(book)
    
    # Upload photos to S3
    prefix = f"books/{book.id}/photos"
    photo_uploads = await upload_files_to_s3(photos, prefix, allowed_photo_types, max_photo_size_mb)
    
    # Store S3 keys in the book record
    photo_s3_keys = [upload["s3_key"] for upload in photo_uploads]
    book.photos_s3_keys = json.dumps(photo_s3_keys)
    
    # Update book with S3 keys
    await db.commit()
    await db.refresh(book)
    
    # In a real app, we would start a background task here to generate the book
    # For this example, we'll just log that we're processing it
    await generate_book_mock(book.id, child_name, adventure_type.value, photo_s3_keys)
    
    return book


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_status(
    book_id: int, 
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get the status of a book.
    
    Args:
        book_id: The ID of the book
        user: The current authenticated user
        db: The database session
        
    Returns:
        BookResponse: The book details
        
    Raises:
        HTTPException: If the book is not found or doesn't belong to the user
    """
    # Get book from database
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    # Check if book exists and belongs to user
    if not book or book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # If book is completed but doesn't have a download URL, generate a presigned URL
    if book.status == BookStatus.COMPLETED and book.pdf_s3_key and not book.download_url:
        book.download_url = generate_presigned_url(book.pdf_s3_key, expires_in=3600)
        await db.commit()
    
    # If book has a thumbnail S3 key but no URL, generate a presigned URL
    if book.thumbnail_s3_key and not book.thumbnail_url:
        book.thumbnail_url = generate_presigned_url(book.thumbnail_s3_key, expires_in=86400)  # 24 hours
        await db.commit()
    
    return book


@router.get("", response_model=BookListResponse)
async def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    List books created by the user.
    
    Args:
        page: The page number (pagination)
        limit: The number of items per page
        user: The current authenticated user
        db: The database session
        
    Returns:
        BookListResponse: Paginated list of books
    """
    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get total number of books for the user
    result = await db.execute(
        select(func.count()).select_from(Book).where(Book.user_id == user.id)
    )
    total = result.scalar()
    
    # Get books for the page
    result = await db.execute(
        select(Book)
        .where(Book.user_id == user.id)
        .order_by(Book.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    books = result.scalars().all()
    
    # Generate presigned URLs for thumbnail and download if needed
    for book in books:
        if book.status == BookStatus.COMPLETED and book.pdf_s3_key and not book.download_url:
            book.download_url = generate_presigned_url(book.pdf_s3_key, expires_in=3600)
        
        if book.thumbnail_s3_key and not book.thumbnail_url:
            book.thumbnail_url = generate_presigned_url(book.thumbnail_s3_key, expires_in=86400)  # 24 hours
    
    # Update books with new URLs
    if books:
        await db.commit()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "books": books
    }


@router.get("/{book_id}/download")
async def download_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Download a book by generating a presigned URL.
    
    Args:
        book_id: The ID of the book
        user: The current authenticated user
        db: The database session
        
    Returns:
        RedirectResponse: Redirect to the download URL
        
    Raises:
        HTTPException: If the book is not found, not completed, or doesn't belong to the user
    """
    # Get book from database
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    # Check if book exists and belongs to user
    if not book or book.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Check if book is completed
    if book.status != BookStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not ready for download"
        )
    
    # If the book doesn't have a PDF S3 key, return an error
    if not book.pdf_s3_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book PDF not available"
        )
    
    # Generate a presigned URL for the PDF
    presigned_url = generate_presigned_url(book.pdf_s3_key, expires_in=3600)
    
    # Update the book with the new download URL
    book.download_url = presigned_url
    await db.commit()
    
    # Redirect to the presigned URL
    return RedirectResponse(url=presigned_url)


@router.post("/{book_id}/webhook-completion", include_in_schema=False)
async def process_book_completion(
    book_id: int,
    status: BookStatus,
    pdf_s3_key: Optional[str] = None,
    thumbnail_s3_key: Optional[str] = None,
    error_message: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Internal webhook for book completion notification.
    In a real app, this would be authenticated with an API key.
    
    Args:
        book_id: The ID of the book
        status: The new status of the book
        pdf_s3_key: The S3 key of the generated PDF
        thumbnail_s3_key: The S3 key of the book thumbnail
        error_message: Error message if the book generation failed
        db: The database session
        
    Returns:
        dict: Confirmation of receipt
    """
    # Get book from database
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update book status and S3 keys
    book.status = status
    
    if status == BookStatus.COMPLETED:
        book.completed_at = datetime.utcnow()
        
        if pdf_s3_key:
            book.pdf_s3_key = pdf_s3_key
            # Generate a presigned URL for the PDF
            book.download_url = generate_presigned_url(pdf_s3_key, expires_in=3600)
        
        if thumbnail_s3_key:
            book.thumbnail_s3_key = thumbnail_s3_key
            # Generate a presigned URL for the thumbnail
            book.thumbnail_url = generate_presigned_url(thumbnail_s3_key, expires_in=86400)  # 24 hours
            
    elif status == BookStatus.FAILED:
        book.error_message = error_message
    
    await db.commit()
    
    return {"received": True} 