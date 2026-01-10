"""
Standalone script to preprocess CSV/XLSX files
Usage: python preprocess_file.py <file_path>
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime


def preprocess_data(df):
    """
    Preprocess the dataframe: remove duplicates, handle missing values,
    encode categorical variables, and normalize numeric columns
    """
    print("\n========== PREPROCESSING STARTED ==========")
    
    rows_before = len(df)
    missing_before = int(df.isnull().sum().sum())
    cols_before = len(df.columns)
    
    print(f"Original shape: {df.shape}")
    print(f"Missing values: {missing_before}")
    
    # Remove duplicates
    df = df.drop_duplicates()
    duplicates_removed = rows_before - len(df)
    print(f"Duplicates removed: {duplicates_removed}")
    
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
    
    print(f"Categorical columns encoded: {len(categorical_cols)}")
    if categorical_cols:
        print(f"  - {', '.join(categorical_cols)}")
    
    # Normalize numeric columns (Min-Max Scaling)
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    for col in numeric_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val != min_val:  # Avoid division by zero
            df[col] = (df[col] - min_val) / (max_val - min_val)
    
    print(f"Numeric columns normalized: {len(numeric_cols)}")
    
    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())
    
    print(f"\nFinal shape: {df.shape}")
    print(f"Missing values after: {missing_after}")
    print("========== PREPROCESSING COMPLETED ==========\n")
    
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


def process_file(file_path, output_dir="processed"):
    """
    Process a CSV or XLSX file and save the preprocessed version
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return None
    
    # Check file extension
    if not file_path.endswith((".csv", ".xlsx")):
        print("Error: Only CSV or Excel files are allowed")
        return None
    
    print(f"Reading file: {file_path}")
    
    # Read file
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None
    
    # Get original filename
    original_filename = os.path.basename(file_path)
    
    # Preprocess the data
    processed_df, stats = preprocess_data(df)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save processed file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"cleaned_{timestamp}_{original_filename.replace('.xlsx', '.csv')}"
    output_path = os.path.join(output_dir, output_filename)
    
    processed_df.to_csv(output_path, index=False)
    
    print(f"✓ Processed file saved to: {output_path}")
    
    return output_path, stats


def main():
    if len(sys.argv) < 2:
        print("Usage: python preprocess_file.py <file_path> [output_dir]")
        print("Example: python preprocess_file.py data.csv")
        print("Example: python preprocess_file.py data.xlsx processed")
        sys.exit(1)
    
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "processed"
    
    result = process_file(file_path, output_dir)
    
    if result:
        print("\n✓ Success! File preprocessing completed.")
    else:
        print("\n✗ Failed to process file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
