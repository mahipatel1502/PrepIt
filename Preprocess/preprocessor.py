"""
Universal Data Preprocessor
Robust preprocessing pipeline that works for all types of datasets
"""
import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder, MinMaxScaler
from scipy.stats import skew

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UniversalPreprocessor:
    """
    Universal data preprocessor that handles all types of datasets intelligently
    """
    
    def __init__(
        self,
        missing_threshold: float = 50.0,
        outlier_method: str = 'cap',
        cardinality_threshold: int = 10,
        scaling_method: str = 'auto'
    ):
        """
        Initialize preprocessor
        
        Args:
            missing_threshold: Drop columns with missing % above this threshold
            outlier_method: 'cap', 'remove', or 'none'
            cardinality_threshold: Threshold for OneHot vs Label encoding
            scaling_method: 'minmax', 'standard', 'robust', or 'auto'
        """
        self.missing_threshold = missing_threshold
        self.outlier_method = outlier_method
        self.cardinality_threshold = cardinality_threshold
        self.scaling_method = scaling_method
        self.metadata = {}
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from CSV or XLSX file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Use CSV or XLSX.")
            
            logger.info(f"Loaded file: {file_path} - Shape: {df.shape}")
            return df
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names"""
        df = df.copy()
        original_cols = df.columns.tolist()
        df.columns = (df.columns
                     .str.lower()
                     .str.strip()
                     .str.replace(' ', '_')
                     .str.replace('-', '_')
                     .str.replace('[^a-z0-9_]', '', regex=True))
        
        # Handle duplicate column names
        seen = {}
        new_cols = []
        for col in df.columns:
            if col in seen:
                seen[col] += 1
                new_cols.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                new_cols.append(col)
        df.columns = new_cols
        
        logger.info(f"Standardized {len(df.columns)} column names")
        return df
    
    def _detect_column_types(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Detect column types automatically"""
        col_types = {
            'datetime': [],
            'id': [],
            'non_informative': [],  # Names, emails, addresses, phone numbers, etc.
            'count': [],
            'categorical': [],
            'numerical': [],
            'boolean': []
        }
        
        # Check if age-related columns exist (to skip redundant birth/death dates)
        age_columns = [col for col in df.columns if any(kw in col.lower() for kw in ['age', '_age', 'age_'])]
        has_age_info = len(age_columns) > 0
        
        for col in df.columns:
            # Check for non-informative identifier columns (names, emails, addresses, phones, URLs, etc.)
            if df[col].dtype == 'object':
                uniqueness_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
                
                # Check if column name suggests it's non-informative
                is_non_informative_name = any(kw in col.lower() for kw in 
                                               ['name', 'email', 'mail', 'phone', 'mobile', 
                                                'address', 'street', 'city', 'zip', 'postal',
                                                'url', 'link', 'website', 'ssn', 'passport',
                                                'license', 'username', 'user_name'])
                
                # If it has a non-informative name AND high uniqueness, drop it
                if is_non_informative_name and uniqueness_ratio > 0.95:
                    col_types['non_informative'].append(col)
                    continue
            
            # Check for ID columns
            if any(kw in col.lower() for kw in ['id', '_id', 'index', 'sno', 'serial']):
                col_types['id'].append(col)
                continue
            
            # Skip birth/death date columns if age information already exists
            if has_age_info and any(kw in col.lower() for kw in ['birth_date', 'death_date', 'dob', 'dod', 'date_of_birth', 'date_of_death']):
                col_types['non_informative'].append(col)
                logger.info(f"Skipping '{col}' - age information already present in dataset")
                continue
            
            # Check for datetime
            if df[col].dtype == 'object':
                if any(kw in col.lower() for kw in ['date', 'time', 'timestamp', 'day', 'dt']):
                    try:
                        temp = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                        if temp.notna().sum() > len(df) * 0.5:
                            col_types['datetime'].append(col)
                            continue
                    except:
                        pass
            
            # Check data type
            if pd.api.types.is_bool_dtype(df[col]):
                col_types['boolean'].append(col)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_types['datetime'].append(col)
            elif pd.api.types.is_numeric_dtype(df[col]):
                # Check if it's a count column
                if any(kw in col.lower() for kw in 
                      ['total', 'count', 'samples', 'negative', 'positive', 'cases', 
                       'tests', 'number', 'amount', 'quantity', 'confirmed', 
                       'recovered', 'deaths', 'sum']):
                    col_types['count'].append(col)
                else:
                    col_types['numerical'].append(col)
            elif df[col].dtype == 'object':
                # Try to convert string numbers to numeric
                try:
                    temp = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
                    if temp.notna().sum() > len(df) * 0.8:
                        col_types['numerical'].append(col)
                    else:
                        col_types['categorical'].append(col)
                except:
                    col_types['categorical'].append(col)
            else:
                col_types['categorical'].append(col)
        
        logger.info(f"Column types detected: {', '.join([f'{k}: {len(v)}' for k, v in col_types.items() if v])}")
        return col_types
    
    def _convert_data_types(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Convert data types appropriately"""
        df = df.copy()
        
        # Convert datetime columns
        for col in col_types['datetime']:
            df[col] = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
        
        # Convert numeric string columns
        for col in col_types['count'] + col_types['numerical']:
            if df[col].dtype == 'object':
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
        
        logger.info("Data types converted successfully")
        return df
    
    def _handle_duplicates(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> Tuple[pd.DataFrame, int]:
        """Remove duplicate rows"""
        df = df.copy()
        initial_rows = len(df)
        
        # For time-series data, remove duplicates based on category + date
        if col_types['datetime'] and col_types['categorical']:
            subset = col_types['categorical'][:1] + col_types['datetime'][:1]
            df = df.drop_duplicates(subset=subset, keep='first')
        else:
            df = df.drop_duplicates()
        
        removed = initial_rows - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate rows")
        
        return df, removed
    
    def _handle_missing_values(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Handle missing values intelligently"""
        df = df.copy()
        
        # Drop columns with too many missing values
        cols_to_drop = []
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > self.missing_threshold:
                cols_to_drop.append(col)
        
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
            logger.info(f"Dropped {len(cols_to_drop)} columns with >{self.missing_threshold}% missing values")
            self.metadata['dropped_columns'] = cols_to_drop
            
            # Update col_types
            for col_type_list in col_types.values():
                for col in cols_to_drop:
                    if col in col_type_list:
                        col_type_list.remove(col)
        
        # Handle missing values by column type
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue
            
            if col in col_types['datetime']:
                # Drop rows with missing critical dates
                df = df.dropna(subset=[col])
            
            elif col in col_types['count']:
                # Group-wise forward fill for time-series
                if col_types['categorical'] and col_types['datetime']:
                    for cat_col in col_types['categorical'][:1]:
                        df[col] = df.groupby(cat_col)[col].transform(lambda x: x.ffill())
                
                # Try to derive from other columns
                if 'total' in col.lower() and df[col].isna().sum() > 0:
                    part_cols = [c for c in col_types['count'] if c != col and 'total' not in c.lower()]
                    if len(part_cols) >= 2:
                        df[col] = df[col].fillna(df[part_cols].sum(axis=1))
                
                elif df[col].isna().sum() > 0:
                    total_cols = [c for c in col_types['count'] if 'total' in c.lower()]
                    if total_cols:
                        total_col = total_cols[0]
                        other_parts = [c for c in col_types['count'] if c != col and c != total_col and 'total' not in c.lower()]
                        if len(other_parts) >= 1:
                            df[col] = df[col].fillna(df[total_col] - df[other_parts].sum(axis=1))
                
                # Fill remaining with 0
                df[col] = df[col].fillna(0)
            
            elif col in col_types['numerical']:
                # Use median for robustness (less affected by outliers)
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
            
            elif col in col_types['categorical']:
                # Use mode (most frequent)
                if not df[col].mode().empty:
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna("Unknown")
            
            elif col in col_types['boolean']:
                # Use mode
                if not df[col].mode().empty:
                    df[col] = df[col].fillna(df[col].mode()[0])
                else:
                    df[col] = df[col].fillna(False)
            
            else:
                # Default: forward fill
                df[col] = df[col].ffill().bfill()
        
        logger.info("Missing values handled successfully")
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Handle outliers using IQR method"""
        if self.outlier_method == 'none':
            return df
        
        df = df.copy()
        numerical_cols = col_types['numerical'] + col_types['count']
        
        for col in numerical_cols:
            if col not in df.columns:
                continue
            
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            
            if outliers > 0:
                if self.outlier_method == 'cap':
                    df[col] = df[col].clip(lower_bound, upper_bound)
                elif self.outlier_method == 'remove':
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        logger.info(f"Outliers handled using method: {self.outlier_method}")
        return df
    
    def _validate_data(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Validate logical constraints"""
        df = df.copy()
        initial_rows = len(df)
        
        # Ensure all counts are non-negative
        for col in col_types['count']:
            if col in df.columns:
                df = df[df[col] >= 0]
        
        # Validate parts don't exceed total
        total_cols = [col for col in col_types['count'] if 'total' in col.lower()]
        if total_cols and len(total_cols) > 0:
            total_col = total_cols[0]
            part_cols = [col for col in col_types['count'] if 'total' not in col.lower() and col != total_col]
            
            if len(part_cols) >= 2 and total_col in df.columns:
                parts_sum = df[part_cols].sum(axis=1)
                # Allow 1% tolerance for rounding
                df = df[parts_sum <= df[total_col] * 1.01]
        
        removed = initial_rows - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} rows with logical inconsistencies")
        
        return df
    
    def _extract_datetime_features(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Extract features from datetime columns"""
        df = df.copy()
        
        for col in col_types['datetime']:
            if col not in df.columns:
                continue
            
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_day'] = df[col].dt.day
            
            logger.info(f"Extracted 3 datetime features from '{col}'")
        
        # Drop original datetime columns
        df = df.drop(columns=col_types['datetime'])
        
        return df
    
    def _engineer_features(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> Tuple[pd.DataFrame, int]:
        """Engineer new features from existing ones"""
        df = df.copy()
        features_created = 0
        
        # Rate features (for count data with totals)
        total_cols = [col for col in col_types['count'] if 'total' in col.lower()]
        if total_cols and len(total_cols) > 0:
            total_col = total_cols[0]
            part_cols = [col for col in col_types['count'] if 'total' not in col.lower() and col != total_col]
            
            if total_col in df.columns:
                for col in part_cols:
                    if col in df.columns:
                        base_name = col.split('_')[0] if '_' in col else col
                        rate_name = f"{base_name}_rate"
                        df[rate_name] = (df[col] / df[total_col].replace(0, 1)).fillna(0)
                        features_created += 1
                
                # Time-series trend features
                if col_types['categorical'] and col_types['datetime']:
                    cat_col = col_types['categorical'][0]
                    
                    for col in part_cols:
                        if col in df.columns:
                            base_name = col.split('_')[0] if '_' in col else col
                            
                            # Daily change
                            change_name = f"{base_name}_daily_change"
                            df[change_name] = df.groupby(cat_col)[col].diff().fillna(0)
                            features_created += 1
                            
                            # 7-day rolling average
                            rolling_name = f"{base_name}_7day_avg"
                            df[rolling_name] = df.groupby(cat_col)[col].transform(
                                lambda x: x.rolling(window=7, min_periods=1).mean()
                            ).fillna(0)
                            features_created += 1
        
        if features_created > 0:
            logger.info(f"Engineered {features_created} new features")
        
        return df, features_created
    
    def _encode_categoricals(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Encode categorical variables - produces only non-negative integers"""
        df = df.copy()
        
        for col in col_types['categorical']:
            if col not in df.columns:
                continue
            
            cardinality = df[col].nunique()
            
            if cardinality <= self.cardinality_threshold:
                # One-hot encoding for low cardinality (0 or 1 only)
                df = pd.get_dummies(df, columns=[col], prefix=col, drop_first=False, dtype='uint8')
                logger.info(f"One-hot encoded '{col}' (cardinality: {cardinality})")
            else:
                # Label encoding for high cardinality (0, 1, 2, 3, ... only)
                encoder = LabelEncoder()
                encoded_name = f'{col}_encoded'
                # LabelEncoder produces non-negative integers starting from 0
                df[encoded_name] = encoder.fit_transform(df[col].astype(str)).astype('int32')
                # Keep original for reference
                logger.info(f"Label encoded '{col}' (cardinality: {cardinality})")
        
        return df
    
    def _scale_features(self, df: pd.DataFrame, col_types: Dict[str, List[str]]) -> pd.DataFrame:
        """Scale numerical features (excluding binary/encoded columns)"""
        df = df.copy()
        
        # Identify columns to scale
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Exclude from scaling:
        # 1. ID columns
        # 2. Encoded categorical columns
        # 3. Date part columns
        # 4. Rate columns (already 0-1)
        # 5. One-hot encoded columns (binary 0/1)
        exclude_cols = (
            col_types['id'] + 
            [col for col in numeric_cols if any(kw in col for kw in ['_encoded', '_year', '_month', '_day', 
                                                                       '_dayofweek', '_quarter', '_week_of_year', 
                                                                       '_rate'])]
        )
        
        # Also exclude one-hot encoded columns (columns with only 0 and 1 values)
        binary_cols = [col for col in numeric_cols 
                      if col not in exclude_cols 
                      and df[col].nunique() <= 2 
                      and set(df[col].unique()).issubset({0, 1, 0.0, 1.0})]
        exclude_cols.extend(binary_cols)
        
        cols_to_scale = [col for col in numeric_cols if col not in exclude_cols]
        
        if not cols_to_scale:
            return df
        
        # Choose scaler based on data distribution
        if self.scaling_method == 'auto':
            # Check skewness to decide
            skewness_vals = [abs(skew(df[col].dropna())) for col in cols_to_scale if len(df[col].dropna()) > 0]
            avg_skewness = np.mean(skewness_vals) if skewness_vals else 0
            
            if avg_skewness > 1:
                scaler = RobustScaler()
                method = 'RobustScaler'
            else:
                scaler = StandardScaler()
                method = 'StandardScaler'
        elif self.scaling_method == 'minmax':
            scaler = MinMaxScaler()
            method = 'MinMaxScaler'
        elif self.scaling_method == 'robust':
            scaler = RobustScaler()
            method = 'RobustScaler'
        else:  # standard
            scaler = StandardScaler()
            method = 'StandardScaler'
        
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        logger.info(f"Scaled {len(cols_to_scale)} columns using {method}")
        logger.info(f"Preserved {len(binary_cols)} binary/one-hot encoded columns (not scaled)")
        
        return df
    
    def _remove_constant_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove constant and duplicate columns"""
        df = df.copy()
        
        # Remove constant columns
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        if constant_cols:
            df = df.drop(columns=constant_cols)
            logger.info(f"Removed {len(constant_cols)} constant columns")
        
        # Remove duplicate columns
        df = df.T.drop_duplicates().T
        
        return df
    
    def preprocess(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Execute full preprocessing pipeline
        
        Args:
            df: Input DataFrame
            target_column: Optional target column name (will be preserved as-is)
            
        Returns:
            Tuple of (processed DataFrame, statistics report)
        """
        original_shape = df.shape
        start_time = datetime.now()
        
        logger.info(f"Starting preprocessing - Input shape: {df.shape}")
        
        # Separate target if provided
        target_data = None
        if target_column and target_column in df.columns:
            target_data = df[target_column].copy()
            df = df.drop(columns=[target_column])
            logger.info(f"Target column '{target_column}' separated for processing")
        
        # Step 1: Standardize column names
        df = self._standardize_columns(df)
        
        # Step 2: Detect column types
        col_types = self._detect_column_types(df)
        
        # Step 2a: Remove non-informative columns (names, emails, etc.)
        if col_types['non_informative']:
            logger.info(f"Removing {len(col_types['non_informative'])} non-informative identifier columns: {col_types['non_informative']}")
            df = df.drop(columns=col_types['non_informative'])
            if 'dropped_columns' not in self.metadata:
                self.metadata['dropped_columns'] = []
            self.metadata['dropped_columns'].extend(col_types['non_informative'])
        
        # Step 3: Convert data types
        df = self._convert_data_types(df, col_types)
        
        # Step 4: Sort time-series data
        if col_types['datetime'] and col_types['categorical']:
            sort_by = col_types['categorical'][:1] + col_types['datetime'][:1]
            df = df.sort_values(by=sort_by).reset_index(drop=True)
            logger.info(f"Sorted time-series data by {sort_by}")
        
        # Step 5: Handle duplicates
        df, duplicates_removed = self._handle_duplicates(df, col_types)
        
        # Step 6: Handle missing values
        df = self._handle_missing_values(df, col_types)
        
        # Step 7: Validate data
        df = self._validate_data(df, col_types)
        
        # Step 8: Handle outliers
        df = self._handle_outliers(df, col_types)
        
        # Step 9: Extract datetime features
        df = self._extract_datetime_features(df, col_types)
        
        # Step 10: Engineer features
        df, features_engineered = self._engineer_features(df, col_types)
        
        # Step 11: Encode categoricals
        df = self._encode_categoricals(df, col_types)
        
        # Step 12: Remove constant/duplicate features
        df = self._remove_constant_features(df)
        
        # Step 13: Fill any remaining NaNs
        df = df.fillna(0)
        
        # Step 14: Scale features
        df = self._scale_features(df, col_types)
        
        # Step 15: Reattach target column if provided
        if target_data is not None:
            df[target_column] = target_data
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Generate report
        report = {
            'original_shape': original_shape,
            'final_shape': df.shape,
            'rows_removed': original_shape[0] - df.shape[0],
            'columns_added': df.shape[1] - original_shape[1],
            'duplicates_removed': duplicates_removed,
            'features_engineered': features_engineered,
            'non_informative_columns_removed': col_types['non_informative'],
            'processing_time_seconds': round(processing_time, 2),
            'column_types': {k: len(v) for k, v in col_types.items()},
            'final_columns': df.columns.tolist(),
            'dropped_columns': self.metadata.get('dropped_columns', []),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Preprocessing completed - Final shape: {df.shape} - Time: {processing_time:.2f}s")
        logger.info(f"Dataset is now ML-ready with {df.shape[1]} features")
        
        return df, report
    
    def fit_transform(
        self,
        file_path: str,
        target_column: Optional[str] = None,
        save_output: bool = True,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load, preprocess, and optionally save the dataset
        
        Args:
            file_path: Path to input file
            target_column: Optional target column name
            save_output: Whether to save processed data
            output_path: Custom output path (default: processed/cleaned_<timestamp>_<filename>.csv)
            
        Returns:
            Dictionary containing processed data, report, and output path
        """
        # Load data
        df = self.load_data(file_path)
        
        # Preprocess
        processed_df, report = self.preprocess(df, target_column)
        
        # Save if requested
        if save_output:
            if output_path is None:
                os.makedirs('processed', exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.basename(file_path)
                output_filename = f"cleaned_{timestamp}_{filename.replace('.xlsx', '.csv').replace('.xls', '.csv')}"
                output_path = os.path.join('processed', output_filename)
            
            processed_df.to_csv(output_path, index=False)
            logger.info(f"Processed data saved to: {output_path}")
            report['output_path'] = output_path
        
        return {
            'data': processed_df,
            'report': report
        }


def preprocess_file(
    file_path: str,
    target_column: Optional[str] = None,
    save_output: bool = True,
    output_path: Optional[str] = None,
    missing_threshold: float = 50.0,
    outlier_method: str = 'cap',
    cardinality_threshold: int = 10,
    scaling_method: str = 'auto'
) -> Dict[str, Any]:
    """
    Convenience function to preprocess a file with one function call
    
    Args:
        file_path: Path to CSV or XLSX file
        target_column: Optional target column name
        save_output: Whether to save processed data
        output_path: Custom output path
        missing_threshold: Threshold for dropping columns (default: 50%)
        outlier_method: 'cap', 'remove', or 'none' (default: 'cap')
        cardinality_threshold: Threshold for OneHot vs Label encoding (default: 10)
        scaling_method: 'auto', 'minmax', 'standard', or 'robust' (default: 'auto')
    
    Returns:
        Dictionary with processed data and report
    """
    preprocessor = UniversalPreprocessor(
        missing_threshold=missing_threshold,
        outlier_method=outlier_method,
        cardinality_threshold=cardinality_threshold,
        scaling_method=scaling_method
    )
    
    return preprocessor.fit_transform(file_path, target_column, save_output, output_path)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python preprocessor.py <file_path> [target_column]")
        print("Example: python preprocessor.py data.csv")
        print("Example: python preprocessor.py data.xlsx target_column_name")
        sys.exit(1)
    
    file_path = sys.argv[1]
    target_col = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = preprocess_file(file_path, target_column=target_col)
        print("\n" + "="*60)
        print("PREPROCESSING COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Output saved to: {result['report']['output_path']}")
        print(f"Original shape: {result['report']['original_shape']}")
        print(f"Final shape: {result['report']['final_shape']}")
        print(f"Processing time: {result['report']['processing_time_seconds']}s")
        print("="*60)
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        sys.exit(1)
