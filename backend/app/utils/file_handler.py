"""
File Validation Utilities
Validates uploaded files for security and integrity
"""
import os
import re
import magic
from fastapi import HTTPException, UploadFile
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "csv,xlsx,xls").split(",")

# Convert MB to bytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and injection attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Remove or replace dangerous characters
    filename = re.sub(r'[^\w\s\-\.]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def validate_file_extension(filename: str) -> str:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        
    Returns:
        File extension (lowercase)
        
    Raises:
        HTTPException if invalid
    """
    if not filename or '.' not in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename - no extension found"
        )
    
    ext = filename.rsplit(".", 1)[-1].lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return ext


def validate_file_size(file_size: int) -> None:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        
    Raises:
        HTTPException if too large
    """
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )
    
    if file_size == 0:
        raise HTTPException(
            status_code=400,
            detail="Empty file not allowed"
        )


def validate_file_content(file_content: bytes, expected_extension: str) -> None:
    """
    Validate file content matches extension using magic numbers
    
    Args:
        file_content: File binary content
        expected_extension: Expected file extension
        
    Raises:
        HTTPException if content doesn't match extension
    """
    try:
        mime = magic.Magic(mime=True)
        detected_mime = mime.from_buffer(file_content)
        
        # Map extensions to expected MIME types
        valid_mimes = {
            "csv": ["text/csv", "text/plain", "application/csv"],
            "xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"],
            "xls": ["application/vnd.ms-excel"]
        }
        
        expected_mimes = valid_mimes.get(expected_extension, [])
        
        if detected_mime not in expected_mimes:
            raise HTTPException(
                status_code=400,
                detail=f"File content doesn't match extension. Detected: {detected_mime}"
            )
    
    except Exception as e:
        # If magic fails, continue (optional validation)
        pass


async def validate_upload_file(file: UploadFile) -> tuple[bytes, str]:
    """
    Comprehensive file validation
    
    Args:
        file: Uploaded file from FastAPI
        
    Returns:
        Tuple of (file_content, sanitized_filename)
        
    Raises:
        HTTPException if validation fails
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    
    # Sanitize filename
    safe_filename = sanitize_filename(file.filename)
    
    # Validate extension
    ext = validate_file_extension(safe_filename)
    
    # Read file content
    file_content = await file.read()
    
    # Validate size
    validate_file_size(len(file_content))
    
    # Validate content matches extension
    validate_file_content(file_content, ext)
    
    return file_content, safe_filename


def validate_file(filename: str):
    """
    Legacy validation function (for backward compatibility)
    """
    validate_file_extension(filename)

