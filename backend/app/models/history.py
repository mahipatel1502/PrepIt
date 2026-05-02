"""
History Data Models
Pydantic models for history-related requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FileInfo(BaseModel):
    """File information model"""
    file_name: str
    bucket_path: str
    file_url: str


class HistoryRecordResponse(BaseModel):
    """History record response model"""
    history_id: str
    user_id: str
    file_id: str
    original_file: FileInfo
    processed_file: Optional[FileInfo] = None
    file_type: str
    status: str
    created_at: str
    preprocessing_version: str
    preprocessing_report: Optional[Dict[str, Any]] = None


class HistorySummary(BaseModel):
    """Simplified history summary for list view"""
    history_id: str
    original_file_name: str
    processed_file_name: Optional[str] = None
    file_type: str
    status: str
    created_at: str


class HistoryListResponse(BaseModel):
    """Response for history list endpoint"""
    status: str
    total_count: int
    returned_count: int
    data: list[HistorySummary]


class HistoryDetailResponse(BaseModel):
    """Response for single history item"""
    status: str
    data: HistoryRecordResponse


class HistoryDeleteResponse(BaseModel):
    """Response for delete operation"""
    status: str
    message: str
    deleted_files: Optional[Dict[str, bool]] = None


class HistoryInsightsResponse(BaseModel):
    """Response model for history insights endpoint"""
    status: str
    data: Dict[str, Any]
