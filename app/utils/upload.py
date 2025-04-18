import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional

# Base directory for file uploads
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_path(directory: str, filename: str, make_unique: bool = True) -> str:
    """
    Generate a file path for an uploaded file.
    
    Args:
        directory: The directory to save to
        filename: The original filename
        make_unique: Whether to make the filename unique
        
    Returns:
        str: The full path to save the file
    """
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Make filename unique if requested
    if make_unique:
        extension = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{extension}"
        return os.path.join(directory, unique_filename)
    
    return os.path.join(directory, filename)


async def save_upload_file(upload_file: UploadFile, directory: str, make_unique: bool = True) -> str:
    """
    Save an uploaded file to disk.
    
    Args:
        upload_file: The uploaded file
        directory: The directory to save to
        make_unique: Whether to make the filename unique
        
    Returns:
        str: The path where the file was saved
    """
    try:
        file_path = get_file_path(directory, upload_file.filename, make_unique)
        
        # Save file to disk
        with open(file_path, "wb") as f:
            f.write(await upload_file.read())
            
        return file_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )


async def save_upload_files(upload_files: List[UploadFile], directory: str, make_unique: bool = True) -> List[str]:
    """
    Save multiple uploaded files to disk.
    
    Args:
        upload_files: The list of uploaded files
        directory: The directory to save to
        make_unique: Whether to make the filenames unique
        
    Returns:
        List[str]: The paths where the files were saved
    """
    paths = []
    for upload_file in upload_files:
        path = await save_upload_file(upload_file, directory, make_unique)
        paths.append(path)
    return paths 