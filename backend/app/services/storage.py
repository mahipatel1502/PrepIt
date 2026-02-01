"""
Supabase Storage Service
Handles file uploads and downloads to/from Supabase buckets
"""
import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Service for managing file storage in Supabase"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        
        # Try service key first (bypasses RLS), then anon key, then legacy SUPABASE_KEY
        self.supabase_key = (
            os.getenv("SUPABASE_SERVICE_KEY") or 
            os.getenv("SUPABASE_ANON_KEY") or 
            os.getenv("SUPABASE_KEY")
        )
        
        self.bucket_originals = os.getenv("SUPABASE_BUCKET_ORIGINALS", "originals")
        self.bucket_processed = os.getenv("SUPABASE_BUCKET_PROCESSED", "processed")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase configuration. "
                "Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file"
            )
        
        # Log which key type is being used
        if os.getenv("SUPABASE_SERVICE_KEY"):
            logger.warning(
                "Using SUPABASE_SERVICE_KEY - this bypasses RLS policies. "
                "Only use in development!"
            )
        
        try:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    def _ensure_buckets_exist(self) -> None:
        """
        Ensure required storage buckets exist
        
        Note: This may fail due to RLS policies. Buckets should be created manually
        in Supabase Dashboard. See SUPABASE_STORAGE_SETUP.md for instructions.
        """
        try:
            # List existing buckets
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets]
            
            # Check if required buckets exist
            missing_buckets = []
            if self.bucket_originals not in bucket_names:
                missing_buckets.append(self.bucket_originals)
            if self.bucket_processed not in bucket_names:
                missing_buckets.append(self.bucket_processed)
            
            if missing_buckets:
                logger.error(
                    f"Required storage buckets not found: {', '.join(missing_buckets)}. "
                    f"Please create them manually in Supabase Dashboard. "
                    f"See SUPABASE_STORAGE_SETUP.md for detailed instructions."
                )
                raise RuntimeError(
                    f"Storage buckets not configured. Missing: {', '.join(missing_buckets)}. "
                    f"Please create buckets in Supabase Dashboard and configure RLS policies. "
                    f"See backend/SUPABASE_STORAGE_SETUP.md for setup instructions."
                )
        
        except RuntimeError:
            # Re-raise RuntimeError (our custom error)
            raise
        except Exception as e:
            # Log other errors but continue (assume buckets exist)
            logger.warning(f"Could not verify buckets: {str(e)}")
    
    def _generate_file_path(self, user_id: str, filename: str, file_id: str, bucket_type: str) -> str:
        """
        Generate storage path for file
        
        Args:
            user_id: User identifier
            filename: Original filename
            file_id: Unique file identifier
            bucket_type: 'original' or 'processed'
            
        Returns:
            Storage path in format: {user_id}/{file_id}_{type}_{filename}
        """
        # Sanitize filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Build path
        path = f"{user_id}/{file_id}_{bucket_type}_{timestamp}_{safe_filename}"
        
        return path
    
    def upload_original_file(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        content_type: str = "application/octet-stream"
    ) -> Tuple[str, str]:
        """
        Upload original file to Supabase storage
        
        Args:
            file_content: File binary content
            filename: Original filename
            user_id: User identifier
            content_type: MIME type
            
        Returns:
            Tuple of (file_id, public_url)
        """
        try:
            self._ensure_buckets_exist()
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Generate storage path
            storage_path = self._generate_file_path(user_id, filename, file_id, "original")
            
            # Upload file
            response = self.client.storage.from_(self.bucket_originals).upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "false"
                }
            )
            
            # Generate public URL (signed URL for private buckets)
            url_response = self.client.storage.from_(self.bucket_originals).create_signed_url(
                storage_path,
                expires_in=86400  # 24 hours
            )
            
            public_url = url_response.get("signedURL", "")
            
            logger.info(f"Uploaded original file: {storage_path}")
            
            return file_id, public_url
        
        except Exception as e:
            logger.error(f"Failed to upload original file: {str(e)}")
            raise RuntimeError(f"Failed to upload original file: {str(e)}")
    
    def upload_processed_file(
        self,
        file_path: str,
        original_filename: str,
        user_id: str,
        file_id: str
    ) -> str:
        """
        Upload processed file to Supabase storage
        
        Args:
            file_path: Path to processed file on disk
            original_filename: Original filename (for reference)
            user_id: User identifier
            file_id: File identifier from original upload
            
        Returns:
            Public URL to processed file
        """
        try:
            self._ensure_buckets_exist()
            
            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Generate storage path
            processed_filename = original_filename.replace(".xlsx", ".csv").replace(".xls", ".csv")
            storage_path = self._generate_file_path(user_id, processed_filename, file_id, "processed")
            
            # Upload file
            response = self.client.storage.from_(self.bucket_processed).upload(
                path=storage_path,
                file=file_content,
                file_options={
                    "content-type": "text/csv",
                    "upsert": "false"
                }
            )
            
            # Generate signed URL
            url_response = self.client.storage.from_(self.bucket_processed).create_signed_url(
                storage_path,
                expires_in=86400  # 24 hours
            )
            
            public_url = url_response.get("signedURL", "")
            
            logger.info(f"Uploaded processed file: {storage_path}")
            
            return public_url
        
        except Exception as e:
            logger.error(f"Failed to upload processed file: {str(e)}")
            raise RuntimeError(f"Failed to upload processed file: {str(e)}")
    
    def delete_file(self, bucket_name: str, file_path: str) -> bool:
        """
        Delete a file from storage
        
        Args:
            bucket_name: Bucket name
            file_path: Path to file in bucket
            
        Returns:
            True if successful
        """
        try:
            self.client.storage.from_(bucket_name).remove([file_path])
            logger.info(f"Deleted file: {bucket_name}/{file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False
    
    def delete_user_files(
        self,
        user_id: str,
        file_id: str
    ) -> Dict[str, bool]:
        """
        Delete both original and processed files for a user
        
        Args:
            user_id: User identifier
            file_id: File identifier
            
        Returns:
            Dictionary with deletion status for each file
        """
        result = {
            "original_deleted": False,
            "processed_deleted": False
        }
        
        try:
            # List files in originals bucket for this user/file_id
            originals_path = f"{user_id}/"
            original_files = self.client.storage.from_(self.bucket_originals).list(originals_path)
            
            # Find and delete original file with matching file_id
            for file in original_files:
                if file_id in file.get("name", ""):
                    file_path = f"{originals_path}{file['name']}"
                    result["original_deleted"] = self.delete_file(self.bucket_originals, file_path)
            
            # List files in processed bucket
            processed_path = f"{user_id}/"
            processed_files = self.client.storage.from_(self.bucket_processed).list(processed_path)
            
            # Find and delete processed file with matching file_id
            for file in processed_files:
                if file_id in file.get("name", ""):
                    file_path = f"{processed_path}{file['name']}"
                    result["processed_deleted"] = self.delete_file(self.bucket_processed, file_path)
            
            logger.info(f"Deleted files for user {user_id}, file_id {file_id}: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Error deleting user files: {str(e)}")
            return result


# Singleton instance
_storage_service: Optional[SupabaseStorageService] = None


def get_storage_service() -> SupabaseStorageService:
    """Get or create storage service singleton"""
    global _storage_service
    
    if _storage_service is None:
        _storage_service = SupabaseStorageService()
    
    return _storage_service
