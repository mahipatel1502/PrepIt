from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from app.services.preprocessing import preprocess_data
from app.services.analytics import analyze_data
from app.utils.file_handler import validate_file

router = APIRouter()

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    validate_file(file.filename)

    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)

    cleaned_df, report = preprocess_data(df)
    analytics = analyze_data(cleaned_df)

    return {
        "message": "Dataset processed successfully",
        "preprocessing_report": report,
        "analytics": analytics
    }
