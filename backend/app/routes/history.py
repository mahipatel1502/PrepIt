"""
History Routes
Handles user preprocessing history tracking and retrieval
"""
from fastapi import APIRouter, HTTPException, Depends, Query
import logging

from app.services.firestore_service import get_firestore_service
from app.services.storage import get_storage_service
from app.utils.auth_middleware import get_current_user
from app.models.history import (
    HistoryListResponse,
    HistoryDetailResponse,
    HistoryDeleteResponse,
    HistoryInsightsResponse,
    HistorySummary,
    HistoryRecordResponse,
    FileInfo
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_history_summary(record: dict) -> HistorySummary:
    """Build response summary from a history record dict."""
    return HistorySummary(
        history_id=record.get("history_id"),
        original_file_name=record.get("original_file", {}).get("file_name", "Unknown"),
        processed_file_name=(
            record.get("processed_file", {}).get("file_name")
            if record.get("processed_file") else None
        ),
        file_type=record.get("file_type", "unknown"),
        status=record.get("status", "unknown"),
        created_at=record.get("created_at", "")
    )


@router.get("", response_model=HistoryListResponse)
async def get_user_history(
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    include_total: bool = Query(
        True,
        description="Include total_count in response (set false to reduce read cost)"
    ),
    current_user: dict = Depends(get_current_user)
):
    """
    Get preprocessing history for the authenticated user
    
    **Authorization:** Bearer token required
    
    **Query Parameters:**
    - limit: Maximum number of records (1-100, default: 50)
    - offset: Pagination offset (default: 0)
    
    **Returns:**
    - List of history records with summary information
    - Total count and returned count
    
    **Security:** Users can only access their own history
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Fetching history for user: {user_id} (limit={limit}, offset={offset})")
        
        # Get Firestore service
        firestore_service = get_firestore_service()
        
        # Fetch history records
        history_records = firestore_service.get_user_history(
            user_id=user_id,
            limit=limit,
            offset=offset,
            summary_only=True
        )
        
        total_count = firestore_service.count_user_history(user_id) if include_total else 0
        
        summaries = [_build_history_summary(record) for record in history_records]
        
        return HistoryListResponse(
            status="success",
            total_count=total_count,
            returned_count=len(summaries),
            data=summaries
        )
    
    except Exception as e:
        logger.error(f"Failed to fetch user history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history: {str(e)}"
        )


@router.get("/completed/files", response_model=HistoryListResponse)
async def get_completed_files(
    limit: int = Query(50, ge=1, le=200, description="Number of completed records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    include_total: bool = Query(
        False,
        description="Include total completed count (set false for lower latency)"
    ),
    current_user: dict = Depends(get_current_user)
):
    """
    Get completed files list for insights/file picker flows.
    Optimized to return summary fields only.
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Fetching completed files for user: {user_id} (limit={limit}, offset={offset})")

        firestore_service = get_firestore_service()
        records = firestore_service.get_user_completed_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        summaries = [_build_history_summary(record) for record in records]
        total_count = firestore_service.count_user_history(user_id, status="success") if include_total else 0

        return HistoryListResponse(
            status="success",
            total_count=total_count,
            returned_count=len(summaries),
            data=summaries
        )

    except Exception as e:
        logger.error(f"Failed to fetch completed files: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch completed files: {str(e)}"
        )


@router.get("/insights/{history_id}", response_model=HistoryInsightsResponse)
async def get_history_insights(
    history_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get lightweight insights for a single processed file.
    Insights are derived from stored preprocessing report (no reprocessing).
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Fetching insights for history: {history_id} user: {user_id}")

        firestore_service = get_firestore_service()
        payload = firestore_service.build_insights_payload(
            history_id=history_id,
            user_id=user_id
        )

        if not payload:
            raise HTTPException(
                status_code=404,
                detail="History record not found or access denied"
            )

        if payload.get("status") != "success":
            raise HTTPException(
                status_code=400,
                detail="Insights are available only for successfully processed files"
            )

        return HistoryInsightsResponse(
            status="success",
            data=payload
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to fetch history insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history insights: {str(e)}"
        )


@router.get("/{history_id}", response_model=HistoryDetailResponse)
async def get_history_detail(
    history_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information for a specific history record
    
    **Authorization:** Bearer token required
    
    **Path Parameters:**
    - history_id: Unique identifier of the history record
    
    **Returns:**
    - Full history record with file URLs and preprocessing report
    
    **Security:** Users can only access their own records
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Fetching history detail: {history_id} for user: {user_id}")
        
        # Get Firestore service
        firestore_service = get_firestore_service()
        
        # Fetch history record
        record = firestore_service.get_history_by_id(
            history_id=history_id,
            user_id=user_id
        )
        
        if not record:
            raise HTTPException(
                status_code=404,
                detail="History record not found or access denied"
            )
        
        # Convert to response model
        original_file = FileInfo(**record.get("original_file", {}))
        
        processed_file = None
        if record.get("processed_file"):
            processed_file = FileInfo(**record["processed_file"])
        
        history_response = HistoryRecordResponse(
            history_id=record.get("history_id"),
            user_id=record.get("user_id"),
            file_id=record.get("file_id"),
            original_file=original_file,
            processed_file=processed_file,
            file_type=record.get("file_type", "unknown"),
            status=record.get("status", "unknown"),
            created_at=record.get("created_at", ""),
            preprocessing_version=record.get("preprocessing_version", "unknown"),
            preprocessing_report=record.get("preprocessing_report")
        )
        
        return HistoryDetailResponse(
            status="success",
            data=history_response
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Failed to fetch history detail: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch history detail: {str(e)}"
        )


@router.delete("/{history_id}", response_model=HistoryDeleteResponse)
async def delete_history_record(
    history_id: str,
    delete_files: bool = Query(
        True,
        description="Also delete files from storage (default: true)"
    ),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a history record and optionally the associated files
    
    **Authorization:** Bearer token required
    
    **Path Parameters:**
    - history_id: Unique identifier of the history record
    
    **Query Parameters:**
    - delete_files: Whether to also delete files from Supabase (default: true)
    
    **Returns:**
    - Deletion status and confirmation
    
    **Security:** Users can only delete their own records
    
    **Warning:** This action cannot be undone
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Deleting history: {history_id} for user: {user_id} (delete_files={delete_files})")
        
        # Get services
        firestore_service = get_firestore_service()
        storage_service = get_storage_service()
        
        # First, get the record to extract file_id
        record = firestore_service.get_history_by_id(
            history_id=history_id,
            user_id=user_id
        )
        
        if not record:
            raise HTTPException(
                status_code=404,
                detail="History record not found or access denied"
            )
        
        file_id = record.get("file_id")
        
        # Delete files from storage if requested
        deleted_files = None
        if delete_files and file_id:
            try:
                deleted_files = storage_service.delete_user_files(
                    user_id=user_id,
                    file_id=file_id
                )
                logger.info(f"Deleted files: {deleted_files}")
            except Exception as e:
                logger.error(f"Failed to delete files: {e}")
                # Continue with history deletion even if file deletion fails
        
        # Delete history record from Firestore
        success = firestore_service.delete_history_record(
            history_id=history_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete history record"
            )
        
        return HistoryDeleteResponse(
            status="success",
            message=f"History record {history_id} deleted successfully",
            deleted_files=deleted_files
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Failed to delete history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete history: {str(e)}"
        )


@router.get("/stats/summary")
async def get_history_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Get statistics summary for user's preprocessing history
    
    **Authorization:** Bearer token required
    
    **Returns:**
    - Total records
    - Successful count
    - Failed count
    - Recent activity
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Fetching history stats for user: {user_id}")
        
        firestore_service = get_firestore_service()
        
        # Fetch only recent activity fields (no need to scan full docs)
        recent_history = firestore_service.get_user_history(
            user_id=user_id,
            limit=5,
            offset=0,
            summary_only=True
        )
        
        # Calculate statistics with count aggregations
        total_count = firestore_service.count_user_history(user_id)
        success_count = firestore_service.count_user_history(user_id, status="success")
        failed_count = total_count - success_count
        
        # Get recent activity (last 5)
        recent_activity = []
        for record in recent_history:
            recent_activity.append({
                "history_id": record.get("history_id"),
                "file_name": record.get("original_file", {}).get("file_name"),
                "status": record.get("status"),
                "created_at": record.get("created_at")
            })
        
        return {
            "status": "success",
            "data": {
                "total_records": total_count,
                "successful_processings": success_count,
                "failed_processings": failed_count,
                "success_rate": round((success_count / total_count * 100) if total_count > 0 else 0, 2),
                "recent_activity": recent_activity
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch history stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch statistics: {str(e)}"
        )
