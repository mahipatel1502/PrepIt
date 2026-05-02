"""
AutoML Models
Pydantic schemas for AutoML module endpoints.
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class AutoMLFileSummary(BaseModel):
    history_id: str
    original_file_name: str
    processed_file_name: Optional[str] = None
    file_type: str
    status: str
    created_at: str


class AutoMLFilesResponse(BaseModel):
    status: str
    returned_count: int
    data: List[AutoMLFileSummary]


class AutoMLColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_pct: float
    unique_count: int
    is_numeric: bool


class AutoMLSchemaData(BaseModel):
    history_id: str
    original_file_name: str
    processed_file_name: Optional[str] = None
    rows: int
    columns: int
    target_candidates: List[str]
    column_profiles: List[AutoMLColumnProfile]


class AutoMLSchemaResponse(BaseModel):
    status: str
    data: AutoMLSchemaData


class AutoMLTrainRequest(BaseModel):
    history_id: str
    target_column: str = Field(min_length=1)
    test_size: float = Field(default=0.2, gt=0.05, lt=0.5)
    random_state: int = Field(default=42, ge=0, le=10_000_000)


class AutoMLLeaderboardEntry(BaseModel):
    rank: Optional[int] = None
    model_key: str
    model_name: str
    fit_time_seconds: Optional[float] = None
    score: Optional[float] = None
    metrics: Dict[str, Optional[float]] = {}
    status: str
    error: Optional[str] = None
    is_best: bool = False


class AutoMLBestModel(BaseModel):
    model_key: str
    model_name: str
    score: float
    metrics: Dict[str, Optional[float]]


class AutoMLTrainData(BaseModel):
    run_id: str
    history_id: str
    original_file_name: str
    processed_file_name: Optional[str] = None
    target_column: str
    problem_type: str
    train_rows: int
    test_rows: int
    feature_count: int
    test_size: float
    leaderboard: List[AutoMLLeaderboardEntry]
    best_model: AutoMLBestModel
    download_endpoint: str
    trained_at: str


class AutoMLTrainResponse(BaseModel):
    status: str
    data: AutoMLTrainData

