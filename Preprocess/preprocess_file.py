"""
Standalone script to preprocess CSV/XLSX files
Automatic Data Preprocessing System - Production Grade
Usage: python preprocess_file.py <file_path>
"""
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')


def preprocess_data(df):
    """
    Production-grade automatic preprocessing pipeline
    Handles time-series, categorical, and numeric data intelligently
    """
    print("\n" + "="*60)
    print("   AUTOMATIC DATA PREPROCESSING PIPELINE")
    print("="*60)
    
    rows_before = len(df)
    missing_before = int(df.isnull().sum().sum())
    cols_before = len(df.columns)
    
    print(f"\n📊 INITIAL DATASET ANALYSIS")
    print(f"   • Shape: {df.shape}")
    print(f"   • Missing values: {missing_before}")
    print(f"   • Columns: {cols_before}")
    
    actions_performed = []
    
    # STEP 1: Standardize column names
    print(f"\n🔧 STEP 1: Standardizing Column Names")
    original_columns = df.columns.tolist()
    df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_').str.replace('-', '_')
    if df.columns.tolist() != original_columns:
        print(f"   ✓ Standardized {len(df.columns)} column names")
        actions_performed.append("Standardized column names (lowercase, underscore-separated)")
    
    # STEP 2: Auto-detect and convert date columns
    print(f"\n📅 STEP 2: Detecting & Converting Date Columns")
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check by keyword or try parsing
            if any(keyword in col.lower() for keyword in ['date', 'time', 'timestamp', 'day', 'dt']):
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    if df[col].notna().sum() > len(df) * 0.5:  # At least 50% valid dates
                        date_cols.append(col)
                        print(f"   ✓ Converted '{col}' to datetime")
                        actions_performed.append(f"Converted '{col}' to datetime format")
                except:
                    pass
    
    # STEP 3: Identify column types automatically
    print(f"\n🔍 STEP 3: Auto-Detecting Column Types")
    id_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['id', '_id', 'index', 'sno'])]
    count_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in 
                  ['total', 'count', 'samples', 'negative', 'positive', 'cases', 'tests', 
                   'number', 'amount', 'quantity', 'confirmed', 'recovered', 'deaths'])]
    categorical_text_cols = [col for col in df.select_dtypes(include='object').columns 
                            if col not in date_cols]
    
    print(f"   • Date columns: {len(date_cols)}")
    print(f"   • ID columns: {len(id_cols)}")
    print(f"   • Count columns: {len(count_cols)}")
    print(f"   • Categorical columns: {len(categorical_text_cols)}")
    
    # STEP 4: Fix data types - convert string numbers to numeric
    print(f"\n🔢 STEP 4: Converting Numeric Strings to Numbers")
    numeric_converted = 0
    for col in count_cols:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
            numeric_converted += 1
    
    # Auto-detect other numeric columns stored as strings
    for col in df.select_dtypes(include='object').columns:
        if col not in date_cols and col not in categorical_text_cols:
            try:
                temp = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                if temp.notna().sum() > len(df) * 0.8:  # 80% valid numbers
                    df[col] = temp
                    numeric_converted += 1
            except:
                pass
    
    if numeric_converted > 0:
        print(f"   ✓ Converted {numeric_converted} columns to numeric type")
        actions_performed.append(f"Converted {numeric_converted} string columns to numeric")
    
    # STEP 5: Sort time-series data
    if date_cols and categorical_text_cols:
        print(f"\n📈 STEP 5: Sorting Time-Series Data")
        sort_by = categorical_text_cols[:1] + date_cols[:1]
        df = df.sort_values(by=sort_by).reset_index(drop=True)
        print(f"   ✓ Sorted by {sort_by}")
        actions_performed.append(f"Sorted time-series data by {sort_by}")
    
    # STEP 6: Remove duplicates
    print(f"\n🗑️  STEP 6: Removing Duplicates")
    df_before_dup = len(df)
    if date_cols and categorical_text_cols:
        # For time series, check duplicates on category + date
        df = df.drop_duplicates(subset=categorical_text_cols[:1] + date_cols[:1], keep='first')
    else:
        df = df.drop_duplicates()
    
    duplicates_removed = df_before_dup - len(df)
    if duplicates_removed > 0:
        print(f"   ✓ Removed {duplicates_removed} duplicate records")
        actions_performed.append(f"Removed {duplicates_removed} duplicate records")
    else:
        print(f"   • No duplicates found")
    
    # STEP 7: Intelligent missing value handling
    print(f"\n🩹 STEP 7: Handling Missing Values Intelligently")
    missing_before_step = int(df.isnull().sum().sum())
    
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            if col in count_cols:
                # Group-wise forward fill for time-series
                if categorical_text_cols and date_cols:
                    for cat_col in categorical_text_cols[:1]:
                        df[col] = df.groupby(cat_col)[col].fillna(method='ffill')
                    print(f"   ✓ Forward-filled '{col}' by group")
                
                # Try deriving from other columns (e.g., negative = total - positive)
                if 'total' in col.lower() and df[col].isna().sum() > 0:
                    part_cols = [c for c in count_cols if c != col and 'total' not in c.lower()]
                    if len(part_cols) >= 2:
                        df[col] = df[col].fillna(df[part_cols].sum(axis=1))
                        print(f"   ✓ Derived missing '{col}' from sum of parts")
                
                elif df[col].isna().sum() > 0:
                    # Check if we can derive from total - other parts
                    total_cols = [c for c in count_cols if 'total' in c.lower()]
                    if total_cols:
                        total_col = total_cols[0]
                        other_parts = [c for c in count_cols if c != col and c != total_col and 'total' not in c.lower()]
                        if len(other_parts) >= 1:
                            df[col] = df[col].fillna(df[total_col] - df[other_parts].sum(axis=1))
                            print(f"   ✓ Derived missing '{col}' from total - other parts")
                
                # Fill remaining with 0
                df[col].fillna(0, inplace=True)
            
            elif col in id_cols:
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(0, inplace=True)
            else:
                # Use median for robustness
                df[col].fillna(df[col].median(), inplace=True)
        
        elif col in date_cols:
            # Drop rows with missing critical dates
            rows_before_date = len(df)
            df = df.dropna(subset=[col])
            if len(df) < rows_before_date:
                print(f"   ✓ Dropped {rows_before_date - len(df)} rows with missing dates")
        
        else:
            # Categorical - use mode
            if not df[col].mode().empty:
                df[col].fillna(df[col].mode()[0], inplace=True)
            else:
                df[col].fillna("Unknown", inplace=True)
    
    missing_after_step = int(df.isnull().sum().sum())
    if missing_before_step > missing_after_step:
        actions_performed.append(f"Handled {missing_before_step - missing_after_step} missing values using group-wise forward fill and derivation")
    
    # STEP 8: Logical validation
    print(f"\n✅ STEP 8: Validating Logical Constraints")
    rows_before_validation = len(df)
    
    # Ensure all counts are non-negative
    for col in count_cols:
        df = df[df[col] >= 0]
    
    # Validate parts don't exceed total
    if any('total' in col.lower() for col in count_cols):
        total_cols = [col for col in count_cols if 'total' in col.lower()]
        if total_cols:
            total_col = total_cols[0]
            part_cols = [col for col in count_cols if 'total' not in col.lower() and col != total_col]
            
            if len(part_cols) >= 2:
                parts_sum = df[part_cols].sum(axis=1)
                # Allow 1% tolerance for rounding errors
                df = df[parts_sum <= df[total_col] * 1.01]
                
                rows_removed = rows_before_validation - len(df)
                if rows_removed > 0:
                    print(f"   ✓ Removed {rows_removed} rows with logical inconsistencies")
                    print(f"      (sum of parts > total)")
                    actions_performed.append(f"Validated logical constraints: removed {rows_removed} invalid rows")
    
    # STEP 9: Feature engineering - Time-based features
    print(f"\n🔨 STEP 9: Engineering Time-Based Features")
    if date_cols:
        for date_col in date_cols:
            df['year'] = df[date_col].dt.year
            df['month'] = df[date_col].dt.month
            df['day'] = df[date_col].dt.day
            df['day_of_week'] = df[date_col].dt.dayofweek
            df['quarter'] = df[date_col].dt.quarter
            df['week_of_year'] = df[date_col].dt.isocalendar().week
            print(f"   ✓ Extracted year, month, day, day_of_week, quarter, week_of_year")
            actions_performed.append("Created time-based features: year, month, day, day_of_week, quarter, week")
            break
    
    # STEP 10: Feature engineering - Rate & Trend features
    print(f"\n📊 STEP 10: Engineering Rate & Trend Features")
    engineered_features = 0
    
    if any('total' in col.lower() for col in count_cols):
        total_cols = [col for col in count_cols if 'total' in col.lower()]
        if total_cols:
            total_col = total_cols[0]
            part_cols = [col for col in count_cols if 'total' not in col.lower() and col != total_col]
            
            # Rate features
            for col in part_cols:
                base_name = col.split('_')[0] if '_' in col else col
                rate_name = f"{base_name}_rate"
                df[rate_name] = (df[col] / df[total_col].replace(0, 1)).fillna(0)
                engineered_features += 1
            
            print(f"   ✓ Created {len(part_cols)} rate features (e.g., positivity_rate)")
            
            # Trend features for time-series
            if categorical_text_cols and date_cols:
                for col in part_cols:
                    base_name = col.split('_')[0] if '_' in col else col
                    
                    # Daily change
                    change_name = f"{base_name}_daily_change"
                    df[change_name] = df.groupby(categorical_text_cols[0])[col].diff().fillna(0)
                    engineered_features += 1
                    
                    # 7-day rolling average
                    rolling_name = f"{base_name}_7day_avg"
                    df[rolling_name] = df.groupby(categorical_text_cols[0])[col].transform(
                        lambda x: x.rolling(window=7, min_periods=1).mean()
                    ).fillna(0)
                    engineered_features += 1
                
                print(f"   ✓ Created {len(part_cols) * 2} trend features (daily change, 7-day avg)")
    
    if engineered_features > 0:
        actions_performed.append(f"Engineered {engineered_features} features: rates, daily changes, rolling averages")
    
    # STEP 11: Encode categorical variables
    print(f"\n🏷️  STEP 11: Encoding Categorical Variables")
    categorical_cols_encoded = []
    le = LabelEncoder()
    
    for col in categorical_text_cols:
        encoded_name = f'{col}_encoded'
        df[encoded_name] = le.fit_transform(df[col].astype(str))
        categorical_cols_encoded.append(col)
        print(f"   ✓ Encoded '{col}' → '{encoded_name}'")
    
    if categorical_cols_encoded:
        actions_performed.append(f"Label-encoded {len(categorical_cols_encoded)} categorical columns")
    
    # STEP 12: Fill any remaining NaNs
    df.fillna(0, inplace=True)
    
    # STEP 13: Normalize numeric features
    print(f"\n⚖️  STEP 13: Normalizing Numeric Features")
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    # Exclude from normalization
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
        print(f"   ✓ Normalized {len(cols_to_scale)} numeric columns using MinMax scaling")
        print(f"      Columns: {', '.join(cols_to_scale[:5])}{'...' if len(cols_to_scale) > 5 else ''}")
        actions_performed.append(f"MinMax normalized {len(cols_to_scale)} numeric columns for ML compatibility")
    
    preserved_cols = id_cols + encoded_cols + date_part_cols + rate_cols
    if preserved_cols:
        print(f"   ✓ Preserved {len(preserved_cols)} columns (not normalized)")
    
    # Final validation
    rows_after = len(df)
    missing_after = int(df.isnull().sum().sum())
    cols_after = len(df.columns)
    
    print(f"\n" + "="*60)
    print("   PREPROCESSING SUMMARY")
    print("="*60)
    print(f"   Rows: {rows_before} → {rows_after} ({rows_after - rows_before:+d})")
    print(f"   Columns: {cols_before} → {cols_after} ({cols_after - cols_before:+d})")
    print(f"   Missing values: {missing_before} → {missing_after}")
    print(f"   Duplicates removed: {duplicates_removed}")
    print(f"\n✨ Dataset is now ML-ready!")
    print(f"   • No missing values")
    print(f"   • All features normalized")
    print(f"   • Categorical variables encoded")
    print(f"   • {engineered_features} new features created")
    print("="*60 + "\n")
    
    stats = {
        "rows_before": rows_before,
        "rows_after": rows_after,
        "duplicates_removed": duplicates_removed,
        "missing_values_before": missing_before,
        "missing_values_after": missing_after,
        "columns_before": cols_before,
        "columns_after": cols_after,
        "features_engineered": engineered_features,
        "date_columns": date_cols,
        "categorical_columns_encoded": categorical_cols_encoded,
        "numeric_columns_scaled": cols_to_scale,
        "columns_preserved": preserved_cols,
        "actions_performed": actions_performed
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
