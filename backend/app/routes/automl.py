"""
AutoML Routes
Standalone endpoints for AutoML file selection, schema discovery, training, and model download.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.models.automl import (
    AutoMLFilesResponse,
    AutoMLSchemaResponse,
    AutoMLTrainRequest,
    AutoMLTrainResponse,
)
from app.services.automl_service import get_automl_service
from app.utils.auth_middleware import get_current_user


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/files", response_model=AutoMLFilesResponse)
async def list_automl_files(
    limit: int = Query(200, ge=1, le=300),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """List user completed files available for AutoML."""
    try:
        user_id = current_user["user_id"]
        service = get_automl_service()
        files = service.list_completed_files(user_id=user_id, limit=limit, offset=offset)
        return {
            "status": "success",
            "returned_count": len(files),
            "data": files,
        }
    except Exception as exc:
        logger.error(f"Failed to list AutoML files: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to list AutoML files: {exc}")


@router.get("/schema/{history_id}", response_model=AutoMLSchemaResponse)
async def get_automl_schema(
    history_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get dataset schema and target candidates for selected processed file."""
    try:
        user_id = current_user["user_id"]
        service = get_automl_service()
        payload = service.get_dataset_schema(user_id=user_id, history_id=history_id)
        return {
            "status": "success",
            "data": payload,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"Failed to load AutoML schema: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to load AutoML schema: {exc}")


@router.post("/train", response_model=AutoMLTrainResponse)
async def train_automl(
    request: AutoMLTrainRequest,
    current_user: dict = Depends(get_current_user),
):
    """Train candidate models and return leaderboard with best model."""
    try:
        user_id = current_user["user_id"]
        service = get_automl_service()
        result = service.train_best_model(
            user_id=user_id,
            history_id=request.history_id,
            target_column=request.target_column,
            test_size=request.test_size,
            random_state=request.random_state,
        )
        return {
            "status": "success",
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.error(f"Failed to train AutoML models: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to train AutoML models: {exc}")


@router.get("/download/{run_id}")
async def download_automl_model(
    run_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Download best-model artifact for the authenticated user."""
    try:
        user_id = current_user["user_id"]
        service = get_automl_service()
        artifact = service.get_artifact_for_user(run_id=run_id, user_id=user_id)

        if not artifact:
            raise HTTPException(status_code=404, detail="Model artifact not found")

        artifact_path, filename = artifact
        return FileResponse(
            path=str(artifact_path),
            media_type="application/octet-stream",
            filename=filename,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to download AutoML model: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to download AutoML model: {exc}")

