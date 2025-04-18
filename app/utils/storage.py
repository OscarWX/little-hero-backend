import os
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta

# Load S3 configuration from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

# Create S3 client
s3_client = boto3.client(
    's3',
    region_name=S3_REGION,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)

def get_s3_key(prefix: str, filename: str) -> str:
    """
    Generate a unique S3 key for a file.
    
    Args:
        prefix: The prefix for the key (folder structure)
        filename: The original filename
        
    Returns:
        str: The generated S3 key
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    extension = os.path.splitext(filename)[1].lower()
    return f"{prefix}/{timestamp}-{unique_id}{extension}"

def validate_file_type(upload_file: UploadFile, allowed_types: List[str]) -> bool:
    """
    Validate that the uploaded file has an allowed content type.
    
    Args:
        upload_file: The file to validate
        allowed_types: List of allowed MIME types
        
    Returns:
        bool: True if the file type is allowed, False otherwise
    """
    content_type = upload_file.content_type
    return content_type in allowed_types

def validate_file_size(upload_file: UploadFile, max_size_mb: int) -> bool:
    """
    Validate that the uploaded file is within the size limit.
    
    Args:
        upload_file: The file to validate
        max_size_mb: Maximum file size in megabytes
        
    Returns:
        bool: True if the file size is within the limit, False otherwise
    """
    # Get file size in bytes
    file_size = 0
    for chunk in upload_file.file:
        file_size += len(chunk)
    
    # Reset file cursor
    upload_file.file.seek(0)
    
    # Convert max size to bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    return file_size <= max_size_bytes

async def upload_file_to_s3(upload_file: UploadFile, prefix: str, allowed_types: Optional[List[str]] = None, max_size_mb: Optional[int] = None) -> Dict[str, Any]:
    """
    Upload a file to S3.
    
    Args:
        upload_file: The file to upload
        prefix: The prefix for the S3 key (folder structure)
        allowed_types: Optional list of allowed MIME types
        max_size_mb: Optional maximum file size in megabytes
        
    Returns:
        Dict[str, Any]: Information about the uploaded file
        
    Raises:
        HTTPException: If upload fails, file type is not allowed, or file size exceeds limit
    """
    try:
        # Validate file type if allowed_types is provided
        if allowed_types and not validate_file_type(upload_file, allowed_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {upload_file.content_type} not allowed. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size if max_size_mb is provided
        if max_size_mb and not validate_file_size(upload_file, max_size_mb):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds the maximum limit of {max_size_mb} MB"
            )
            
        # Generate a unique key for the file
        s3_key = get_s3_key(prefix, upload_file.filename)
        
        # Upload the file
        file_content = await upload_file.read()
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=upload_file.content_type
        )
        
        # Reset file cursor in case it needs to be read again
        await upload_file.seek(0)
        
        # Return file information
        return {
            "s3_key": s3_key,
            "original_filename": upload_file.filename,
            "content_type": upload_file.content_type,
            "size": len(file_content)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file to S3: {str(e)}"
        )

async def upload_files_to_s3(files: List[UploadFile], prefix: str, allowed_types: Optional[List[str]] = None, max_size_mb: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Upload multiple files to S3.
    
    Args:
        files: The files to upload
        prefix: The prefix for the S3 keys (folder structure)
        allowed_types: Optional list of allowed MIME types
        max_size_mb: Optional maximum file size in megabytes
        
    Returns:
        List[Dict[str, Any]]: Information about the uploaded files
    """
    results = []
    for file in files:
        result = await upload_file_to_s3(file, prefix, allowed_types, max_size_mb)
        results.append(result)
    return results

def upload_bytes_to_s3(data: bytes, prefix: str, filename: str, content_type: str) -> Dict[str, Any]:
    """
    Upload bytes to S3.
    
    Args:
        data: The data to upload
        prefix: The prefix for the S3 key (folder structure)
        filename: The filename to use
        content_type: The content type of the data
        
    Returns:
        Dict[str, Any]: Information about the uploaded file
        
    Raises:
        HTTPException: If upload fails
    """
    try:
        # Generate a unique key for the file
        s3_key = get_s3_key(prefix, filename)
        
        # Upload the data
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=data,
            ContentType=content_type
        )
        
        # Return file information
        return {
            "s3_key": s3_key,
            "original_filename": filename,
            "content_type": content_type,
            "size": len(data)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload data to S3: {str(e)}"
        )

def generate_presigned_url(s3_key: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL for an S3 object.
    
    Args:
        s3_key: The S3 key of the object
        expires_in: Time in seconds until the URL expires
        
    Returns:
        str: The presigned URL
        
    Raises:
        HTTPException: If generating the URL fails
    """
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=expires_in
        )
        return response
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )

def delete_file_from_s3(s3_key: str) -> bool:
    """
    Delete a file from S3.
    
    Args:
        s3_key: The S3 key of the file to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key
        )
        return True
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file from S3: {str(e)}"
        )

def delete_files_from_s3(s3_keys: List[str]) -> bool:
    """
    Delete multiple files from S3.
    
    Args:
        s3_keys: The S3 keys of the files to delete
        
    Returns:
        bool: True if deletion was successful
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        # S3 batch delete requires a specific format
        objects = [{'Key': key} for key in s3_keys]
        
        s3_client.delete_objects(
            Bucket=S3_BUCKET_NAME,
            Delete={
                'Objects': objects
            }
        )
        return True
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete files from S3: {str(e)}"
        )

def configure_lifecycle_policy():
    """
    Configure a lifecycle policy for the S3 bucket to automatically delete
    temporary files after a specified time period.
    
    This is typically run once during application setup.
    """
    try:
        lifecycle_config = {
            'Rules': [
                {
                    'ID': 'Delete temporary uploads',
                    'Status': 'Enabled',
                    'Prefix': 'temp/',
                    'Expiration': {'Days': 1}  # Delete temp files after 1 day
                },
                {
                    'ID': 'Delete processing files',
                    'Status': 'Enabled',
                    'Prefix': 'processing/',
                    'Expiration': {'Days': 7}  # Delete processing files after 7 days
                }
            ]
        }
        
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=S3_BUCKET_NAME,
            LifecycleConfiguration=lifecycle_config
        )
        return True
    except Exception as e:
        print(f"Failed to configure lifecycle policy: {str(e)}")
        return False 