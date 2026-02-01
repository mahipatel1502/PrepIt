"""
Firebase Firestore Service
Manages user history records in Firestore
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from firebase_admin import firestore
from app.utils.firebase_config import initialize_firebase

logger = logging.getLogger(__name__)

# Initialize Firebase (this ensures Firestore is available)
initialize_firebase()


class FirestoreService:
    """Service for managing Firestore database operations"""
    
    COLLECTION_HISTORY = "preprocessing_history"
    PREPROCESSING_VERSION = "v2.0"
    
    def __init__(self):
        """Initialize Firestore client"""
        try:
            self.db = firestore.client()
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {str(e)}")
            raise RuntimeError(f"Failed to initialize Firestore: {str(e)}")
    
    def create_history_record(
        self,
        user_id: str,
        file_id: str,
        original_file_name: str,
        original_bucket_path: str,
        original_file_url: str,
        processed_file_name: Optional[str] = None,
        processed_bucket_path: Optional[str] = None,
        processed_file_url: Optional[str] = None,
        file_type: str = "csv",
        status: str = "success",
        preprocessing_report: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new history record in Firestore
        
        Args:
            user_id: Firebase user UUID
            file_id: Unique file identifier
            original_file_name: Original filename
            original_bucket_path: Path in Supabase bucket
            original_file_url: Signed URL for original file
            processed_file_name: Processed filename (None if failed)
            processed_bucket_path: Processed file path (None if failed)
            processed_file_url: Signed URL for processed file (None if failed)
            file_type: File extension (csv, xlsx, xls)
            status: Processing status (success, failed)
            preprocessing_report: Full preprocessing report
            
        Returns:
            history_id: Generated document ID
        """
        try:
            # Prepare history document
            history_data = {
                "user_id": user_id,
                "file_id": file_id,
                "original_file": {
                    "file_name": original_file_name,
                    "bucket_path": original_bucket_path,
                    "file_url": original_file_url
                },
                "file_type": file_type,
                "status": status,
                "created_at": firestore.SERVER_TIMESTAMP,
                "preprocessing_version": self.PREPROCESSING_VERSION
            }
            
            # Add processed file info only if successful
            if status == "success" and processed_file_name:
                history_data["processed_file"] = {
                    "file_name": processed_file_name,
                    "bucket_path": processed_bucket_path,
                    "file_url": processed_file_url
                }
            
            # Add preprocessing report if available
            if preprocessing_report:
                history_data["preprocessing_report"] = preprocessing_report
            
            # Create document with auto-generated ID
            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document()
            doc_ref.set(history_data)
            
            history_id = doc_ref.id
            logger.info(f"Created history record: {history_id} for user: {user_id}")
            
            return history_id
        
        except Exception as e:
            logger.error(f"Failed to create history record: {str(e)}")
            raise RuntimeError(f"Failed to create history record: {str(e)}")
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get preprocessing history for a specific user
        
        Args:
            user_id: Firebase user UUID
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)
            
        Returns:
            List of history records
        """
        try:
            # Query history collection filtered by user_id
            query = (
                self.db.collection(self.COLLECTION_HISTORY)
                .where("user_id", "==", user_id)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .offset(offset)
            )
            
            docs = query.stream()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                data["history_id"] = doc.id
                
                # Convert Firestore timestamp to ISO format
                if "created_at" in data and data["created_at"]:
                    data["created_at"] = data["created_at"].isoformat()
                
                history.append(data)
            
            logger.info(f"Retrieved {len(history)} history records for user: {user_id}")
            return history
        
        except Exception as e:
            logger.error(f"Failed to get user history: {str(e)}")
            raise RuntimeError(f"Failed to get user history: {str(e)}")
    
    def get_history_by_id(
        self,
        history_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single history record by ID
        Ensures user can only access their own records
        
        Args:
            history_id: History document ID
            user_id: Firebase user UUID (for verification)
            
        Returns:
            History record or None if not found/unauthorized
        """
        try:
            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document(history_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"History record not found: {history_id}")
                return None
            
            data = doc.to_dict()
            
            # Security check: ensure user owns this record
            if data.get("user_id") != user_id:
                logger.warning(
                    f"Unauthorized access attempt: user {user_id} "
                    f"tried to access history {history_id}"
                )
                return None
            
            data["history_id"] = doc.id
            
            # Convert timestamp
            if "created_at" in data and data["created_at"]:
                data["created_at"] = data["created_at"].isoformat()
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to get history by ID: {str(e)}")
            raise RuntimeError(f"Failed to get history by ID: {str(e)}")
    
    def delete_history_record(
        self,
        history_id: str,
        user_id: str
    ) -> bool:
        """
        Delete a history record
        Ensures user can only delete their own records
        
        Args:
            history_id: History document ID
            user_id: Firebase user UUID (for verification)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # First verify ownership
            doc_ref = self.db.collection(self.COLLECTION_HISTORY).document(history_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logger.warning(f"History record not found: {history_id}")
                return False
            
            data = doc.to_dict()
            
            # Security check
            if data.get("user_id") != user_id:
                logger.warning(
                    f"Unauthorized delete attempt: user {user_id} "
                    f"tried to delete history {history_id}"
                )
                return False
            
            # Delete the document
            doc_ref.delete()
            logger.info(f"Deleted history record: {history_id} for user: {user_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete history record: {str(e)}")
            raise RuntimeError(f"Failed to delete history record: {str(e)}")
    
    def count_user_history(self, user_id: str) -> int:
        """
        Count total number of history records for a user
        
        Args:
            user_id: Firebase user UUID
            
        Returns:
            Total count
        """
        try:
            query = (
                self.db.collection(self.COLLECTION_HISTORY)
                .where("user_id", "==", user_id)
            )
            
            docs = list(query.stream())
            count = len(docs)
            
            logger.info(f"User {user_id} has {count} history records")
            return count
        
        except Exception as e:
            logger.error(f"Failed to count user history: {str(e)}")
            return 0


# Singleton instance
_firestore_service: Optional[FirestoreService] = None


def get_firestore_service() -> FirestoreService:
    """Get or create Firestore service singleton"""
    global _firestore_service
    
    if _firestore_service is None:
        _firestore_service = FirestoreService()
    
    return _firestore_service
