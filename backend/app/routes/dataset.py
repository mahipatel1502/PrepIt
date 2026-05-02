"""
Dataset Routes
Handles file upload, preprocessing, and storage
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from typing import Optional
import logging

from app.services.storage import get_storage_service
from app.services.preprocessing_orchestrator import create_preprocessor
from app.services.firestore_service import get_firestore_service
from app.utils.file_handler import validate_upload_file
from app.utils.auth_middleware import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_and_process_dataset(
    file: UploadFile = File(..., description="CSV or Excel file to process"),
    target_column: Optional[str] = Form(None, description="Target column name (optional)"),
    missing_threshold: float = Form(50.0, description="Threshold for dropping columns with missing values (%)"),
    outlier_method: str = Form('cap', description="Outlier handling method: 'cap', 'remove', or 'none'"),
    cardinality_threshold: int = Form(10, description="Threshold for OneHot vs Label encoding"),
    scaling_method: str = Form('auto', description="Scaling method: 'auto', 'minmax', 'standard', or 'robust'"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and preprocess a dataset
    
    **Flow:**
    1. Validate and upload original file to Supabase
    2. Preprocess using existing preprocessor.py
    3. Upload processed file to Supabase
    4. Return download URLs for both files
    
    **Requires:** Bearer token in Authorization header
    
    **Returns:**
    - original_file_url: Download link for original file
    - processed_file_url: Download link for processed file
    - preprocessing_report: Detailed report from preprocessor
    """
    preprocessor = None
    
    try:
        # Step 1: Validate uploaded file
        logger.info(f"Validating file: {file.filename}")
        file_content, safe_filename = await validate_upload_file(file)
        
        user_id = current_user['user_id']
        
        # Step 2: Upload original file to Supabase
        logger.info("Uploading original file to Supabase")
        storage_service = get_storage_service()
        
        try:
            file_id, original_file_url = storage_service.upload_original_file(
                file_content=file_content,
                filename=safe_filename,
                user_id=user_id,
                content_type=file.content_type or "application/octet-stream"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload original file: {str(e)}"
            )
        
        # Determine file type
        file_type = safe_filename.rsplit(".", 1)[-1].lower()
        
        # Step 3: Preprocess file using preprocessor.py
        logger.info("Starting preprocessing pipeline")
        preprocessor = create_preprocessor()
        
        preprocessing_result = preprocessor.process_file(
            file_content=file_content,
            filename=safe_filename,
            target_column=target_column,
            missing_threshold=missing_threshold,
            outlier_method=outlier_method,
            cardinality_threshold=cardinality_threshold,
            scaling_method=scaling_method
        )
        
        # Initialize Firestore service
        firestore_service = get_firestore_service()
        
        # Check if preprocessing succeeded
        if not preprocessing_result['success']:
            error_msg = preprocessing_result.get('error', 'Unknown preprocessing error')
            logger.error(f"Preprocessing failed: {error_msg}")
            
            # Save history record with failed status
            try:
                # Get original file bucket path (reconstruct from URL or use pattern)
                original_bucket_path = f"{user_id}/{file_id}_original_{safe_filename}"
                
                history_id = firestore_service.create_history_record(
                    user_id=user_id,
                    file_id=file_id,
                    original_file_name=safe_filename,
                    original_bucket_path=original_bucket_path,
                    original_file_url=original_file_url,
                    file_type=file_type,
                    status="failed"
                )
                logger.info(f"Created failed history record: {history_id}")
            except Exception as e:
                logger.error(f"Failed to save history record: {e}")
            
            # Original file is still stored - return partial success
            return {
                "status": "error",
                "error_code": "PREPROCESSING_FAILED",
                "message": f"Preprocessing failed: {error_msg}",
                "original_file_url": original_file_url,
                "processed_file_url": None,
                "preprocessing_report": None
            }
        
        # Step 4: Upload processed file to Supabase
        logger.info("Uploading processed file to Supabase")
        processed_file_path = preprocessing_result['processed_file_path']
        
        try:
            processed_file_url = storage_service.upload_processed_file(
                file_path=processed_file_path,
                original_filename=safe_filename,
                user_id=user_id,
                file_id=file_id
            )
        except Exception as e:
            logger.error(f"Failed to upload processed file: {str(e)}")
            
            # Save history with failed processed upload
            try:
                original_bucket_path = f"{user_id}/{file_id}_original_{safe_filename}"
                
                history_id = firestore_service.create_history_record(
                    user_id=user_id,
                    file_id=file_id,
                    original_file_name=safe_filename,
                    original_bucket_path=original_bucket_path,
                    original_file_url=original_file_url,
                    file_type=file_type,
                    status="failed",
                    preprocessing_report=preprocessing_result['report']
                )
            except Exception as hist_err:
                logger.error(f"Failed to save history: {hist_err}")
            
            # Original file is stored, preprocessing succeeded, but upload failed
            return {
                "status": "error",
                "error_code": "PROCESSED_UPLOAD_FAILED",
                "message": f"Processed file upload failed: {str(e)}",
                "original_file_url": original_file_url,
                "processed_file_url": None,
                "preprocessing_report": preprocessing_result['report']
            }
        
        # Step 5: Save successful history record to Firestore
        history_id = None
        try:
            processed_filename = safe_filename.replace(".xlsx", ".csv").replace(".xls", ".csv")
            original_bucket_path = f"{user_id}/{file_id}_original_{safe_filename}"
            processed_bucket_path = f"{user_id}/{file_id}_processed_{processed_filename}"
            
            history_id = firestore_service.create_history_record(
                user_id=user_id,
                file_id=file_id,
                original_file_name=safe_filename,
                original_bucket_path=original_bucket_path,
                original_file_url=original_file_url,
                processed_file_name=processed_filename,
                processed_bucket_path=processed_bucket_path,
                processed_file_url=processed_file_url,
                file_type=file_type,
                status="success",
                preprocessing_report=preprocessing_result['report']
            )
            logger.info(f"Created history record: {history_id}")
        except Exception as e:
            logger.error(f"Failed to save history record for successful upload: {e}")
            raise HTTPException(
                status_code=500,
                detail=(
                    "File processed but failed to save history record. "
                    "Please retry upload or contact support."
                )
            )
        
        # Step 6: Return success response
        logger.info("Pipeline completed successfully")
        
        return {
            "status": "success",
            "original_file_url": original_file_url,
            "processed_file_url": processed_file_url,
            "preprocessing_report": preprocessing_result['report'],
            "history_id": history_id,
            "message": "File processed successfully"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in upload pipeline: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )
    
    finally:
        # Step 6: Cleanup temporary files
        if preprocessor:
            try:
                preprocessor.cleanup()
                logger.info("Temporary files cleaned up")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp files: {e}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for dataset service
    """
    return {
        "status": "healthy",
        "service": "dataset-preprocessing",
        "version": "2.0.0"
    }

