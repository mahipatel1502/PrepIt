from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = FastAPI()

class FilePathRequest(BaseModel):
    file_path: str

PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)


@app.post("/api/process-file-path")
async def process_file_from_path(request: FilePathRequest):
    """
    Process a CSV or XLSX file from a given file path
    """
    file_path = request.file_path
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    
    # Check file extension
    if not file_path.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")
    
    # Read file
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Get original filename
    original_filename = os.path.basename(file_path)
    
    # Preprocess the data
    processed_df, stats = preprocess_data(df)
    
    # Save processed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"cleaned_{timestamp}_{original_filename.replace('.xlsx', '.csv')}"  
    output_path = os.path.join(PROCESSED_DIR, output_filename)
    processed_df.to_csv(output_path, index=False)
    
    return {
        "message": "File processed and saved successfully",
        "input_file": file_path,
        "output_file": output_path,
        "statistics": stats
    }


def preprocess_data(df):
    """
    Preprocess the dataframe: remove duplicates, handle missing values,
    encode categorical variables, and normalize numeric columns
    """
    rows_before = len(df)
    missing_before = int(df.isnull().sum().sum())
    cols_before = len(df.columns)
    
    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = rows_before - len(df)
    
    # Handle missing values
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            # Fill numeric columns with mean
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            # Fill categorical columns with mode
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna("Unknown", inplace=True)
    
    # Encode categorical columns
    categorical_cols = []
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("category").cat.codes
        categorical_cols.append(col)
    
    # Normalize numeric columns (Min-Max Scaling)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    for col in numeric_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val != min_val:  # Avoid division by zero
            df[col] = (df[col] - min_val) / (max_val - min_val)
    
    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())
    
    stats = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicates_removed,
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "columns": cols_before,
        "categorical_columns_encoded": categorical_cols,
        "numeric_columns_normalized": numeric_cols
    }
    
    return df, stats


@app.get("/")
def root():
    return {"status": "Backend running"}
