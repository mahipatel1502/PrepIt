from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd

from app.services.preprocessing import preprocess_data
from app.services.analytics import analyze_data
from app.utils.file_handler import validate_file
from app.utils.auth_middleware import get_current_user

router = APIRouter()

@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process a dataset (CSV or Excel)
    
    Requires: Bearer token in Authorization header
    """
    validate_file(file.filename)

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)

    cleaned_df, report = preprocess_data(df)
    analytics = analyze_data(cleaned_df)

    return {
        "message": "Dataset processed successfully",
        "user_id": current_user['user_id'],
        "preprocessing_report": report,
        "analytics": analytics
    }
