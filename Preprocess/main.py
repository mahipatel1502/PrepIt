from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
from datetime import datetime
from io import BytesIO
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

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


@app.post("/api/process-file-upload")
async def process_file_upload(file: UploadFile = File(...)):
    """
    Process a CSV or XLSX file from file upload
    """
    # Check file extension
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV or Excel files are allowed")
    
    # Read file
    try:
        contents = await file.read()
        if file.filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    # Get original filename
    original_filename = file.filename
    
    # Preprocess the data
    processed_df, stats = preprocess_data(df)
    
    # Save processed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"cleaned_{timestamp}_{original_filename.replace('.xlsx', '.csv')}"  
    output_path = os.path.join(PROCESSED_DIR, output_filename)
    processed_df.to_csv(output_path, index=False)
    
    return {
        "message": "File processed and saved successfully",
        "input_file": original_filename,
        "output_file": output_path,
        "statistics": stats
    }


def preprocess_data(df):
    """
    Production-grade automatic preprocessing pipeline for API
    """
    rows_before = len(df)
    missing_before = int(df.isnull().sum().sum())
    cols_before = len(df.columns)
    
    actions_performed = []
    
    # 1️⃣ Standardize column names
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
    actions_performed.append("Standardized column names")
    
    # 2️⃣ Auto-detect and convert date columns
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'object' and any(kw in col.lower() for kw in ['date', 'time', 'timestamp', 'day', 'dt']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                if df[col].notna().sum() > len(df) * 0.5:
                    date_cols.append(col)
                    actions_performed.append(f"Converted '{col}' to datetime")
            except:
                pass
    
    # 3️⃣ Identify column types
    id_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['id', '_id', 'index', 'sno'])]
    count_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in 
                  ['total', 'count', 'samples', 'negative', 'positive', 'cases', 'tests', 
                   'number', 'amount', 'quantity', 'confirmed', 'recovered', 'deaths'])]
    categorical_text_cols = [col for col in df.select_dtypes(include='object').columns 
                            if col not in date_cols]
    
    # 4️⃣ Fix data types
    for col in count_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    for col in df.select_dtypes(include='object').columns:
        if col not in date_cols and col not in categorical_text_cols:
            try:
                temp = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                if temp.notna().sum() > len(df) * 0.8:
                    df[col] = temp
            except:
                pass
    
    # 5️⃣ Sort time-series
    if date_cols and categorical_text_cols:
        sort_by = categorical_text_cols[:1] + date_cols[:1]
        df = df.sort_values(by=sort_by).reset_index(drop=True)
        actions_performed.append(f"Sorted by {sort_by}")
    
    # 6️⃣ Remove duplicates
    if date_cols and categorical_text_cols:
        df = df.drop_duplicates(subset=categorical_text_cols[:1] + date_cols[:1], keep='first')
    else:
        df = df.drop_duplicates()
    duplicates_removed = rows_before - len(df)
    
    # 7️⃣ Handle missing values
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            if col in count_cols:
                if categorical_text_cols and date_cols:
                    for cat_col in categorical_text_cols[:1]:
                        df[col] = df.groupby(cat_col)[col].fillna(method='ffill')
                
                if 'total' in col.lower() and df[col].isna().sum() > 0:
                    part_cols = [c for c in count_cols if c != col and 'total' not in c.lower()]
                    if len(part_cols) >= 2:
                        df[col] = df[col].fillna(df[part_cols].sum(axis=1))
                elif df[col].isna().sum() > 0:
                    total_cols = [c for c in count_cols if 'total' in c.lower()]
                    if total_cols:
                        total_col = total_cols[0]
                        other_parts = [c for c in count_cols if c != col and c != total_col and 'total' not in c.lower()]
                        if len(other_parts) >= 1:
                            df[col] = df[col].fillna(df[total_col] - df[other_parts].sum(axis=1))
                
                df[col].fillna(0, inplace=True)
            elif col in id_cols:
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(0, inplace=True)
            else:
                df[col].fillna(df[col].median(), inplace=True)
        elif col in date_cols:
            df = df.dropna(subset=[col])
        else:
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna("Unknown", inplace=True)
    
    # 8️⃣ Logical validation
    for col in count_cols:
        df = df[df[col] >= 0]
    
    if any('total' in col.lower() for col in count_cols):
        total_cols = [col for col in count_cols if 'total' in col.lower()]
        if total_cols:
            total_col = total_cols[0]
            part_cols = [col for col in count_cols if 'total' not in col.lower() and col != total_col]
            if len(part_cols) >= 2:
                parts_sum = df[part_cols].sum(axis=1)
                df = df[parts_sum <= df[total_col] * 1.01]
    
    # 9️⃣ Feature engineering
    engineered_features = 0
    if date_cols:
        for date_col in date_cols:
            df['year'] = df[date_col].dt.year
            df['month'] = df[date_col].dt.month
            df['day'] = df[date_col].dt.day
            df['day_of_week'] = df[date_col].dt.dayofweek
            df['quarter'] = df[date_col].dt.quarter
            df['week_of_year'] = df[date_col].dt.isocalendar().week
            engineered_features += 6
            break
    
    if any('total' in col.lower() for col in count_cols):
        total_cols = [col for col in count_cols if 'total' in col.lower()]
        if total_cols:
            total_col = total_cols[0]
            part_cols = [col for col in count_cols if 'total' not in col.lower() and col != total_col]
            
            for col in part_cols:
                base_name = col.split('_')[0] if '_' in col else col
                rate_name = f"{base_name}_rate"
                df[rate_name] = (df[col] / df[total_col].replace(0, 1)).fillna(0)
                engineered_features += 1
            
            if categorical_text_cols and date_cols:
                for col in part_cols:
                    base_name = col.split('_')[0] if '_' in col else col
                    change_name = f"{base_name}_daily_change"
                    df[change_name] = df.groupby(categorical_text_cols[0])[col].diff().fillna(0)
                    rolling_name = f"{base_name}_7day_avg"
                    df[rolling_name] = df.groupby(categorical_text_cols[0])[col].transform(
                        lambda x: x.rolling(window=7, min_periods=1).mean()
                    ).fillna(0)
                    engineered_features += 2
    
    actions_performed.append(f"Engineered {engineered_features} features")
    
    # 🔟 Encode categoricals
    categorical_cols_encoded = []
    le = LabelEncoder()
    for col in categorical_text_cols:
        encoded_name = f'{col}_encoded'
        df[encoded_name] = le.fit_transform(df[col].astype(str))
        categorical_cols_encoded.append(col)
    
    df.fillna(0, inplace=True)
    
    # 1️⃣1️⃣ Normalize
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    encoded_cols = [col for col in numeric_cols if 'encoded' in col]
    date_part_cols = ['year', 'month', 'day', 'day_of_week', 'quarter', 'week_of_year']
    rate_cols = [col for col in numeric_cols if '_rate' in col]
    
    cols_to_scale = [col for col in numeric_cols 
                     if col not in id_cols 
                     and col not in encoded_cols
                     and col not in date_part_cols
                     and col not in rate_cols]
    
    scaler = MinMaxScaler()
    if cols_to_scale:
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    
    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())
    
    stats = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicates_removed,
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "columns_before": cols_before,
        "columns_after": len(df.columns),
        "features_engineered": engineered_features,
        "date_columns": date_cols,
        "categorical_columns_encoded": categorical_cols_encoded,
        "numeric_columns_scaled": cols_to_scale,
        "columns_preserved": id_cols + encoded_cols + date_part_cols + rate_cols,
        "actions_performed": actions_performed
    }
    
    return df, stats


@app.get("/")
def root():
    return {"status": "Backend running"}
