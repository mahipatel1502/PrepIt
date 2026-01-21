import os
import logging
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from scipy.stats import skew
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataProfiler:
    """Analyze and profile input data to detect types and characteristics."""
    
    @staticmethod
    def profile_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Profile the dataset to identify column types and characteristics.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary containing profiling information
        """
        profile = {
            'shape': df.shape,
            'columns': {},
            'missing_percentage': {},
            'cardinality': {},
            'skewness': {},
            'duplicates': df.duplicated().sum()
        }
        
        for col in df.columns:
            profile['missing_percentage'][col] = (df[col].isnull().sum() / len(df)) * 100
            
            if df[col].dtype == 'object':
                profile['columns'][col] = 'categorical'
                profile['cardinality'][col] = df[col].nunique()
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                profile['columns'][col] = 'datetime'
            elif pd.api.types.is_bool_dtype(df[col]):
                profile['columns'][col] = 'boolean'
            elif pd.api.types.is_numeric_dtype(df[col]):
                profile['columns'][col] = 'numerical'
                profile['skewness'][col] = abs(skew(df[col].dropna()))
            else:
                profile['columns'][col] = 'unknown'
        
        logger.info(f"Data profiling completed. Shape: {df.shape}")
        return profile


class MissingValueHandler:
    """Handle missing values based on data characteristics."""
    
    def __init__(self, missing_threshold: float = 40.0):
        """
        Initialize missing value handler.
        
        Args:
            missing_threshold: Drop columns with missing % above this threshold
        """
        self.missing_threshold = missing_threshold
        self.columns_dropped = []
        self.imputation_strategy = {}
    
    def handle_missing(
        self, 
        df: pd.DataFrame, 
        profile: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Handle missing values intelligently.
        
        Args:
            df: Input DataFrame
            profile: Data profile information
            
        Returns:
            Tuple of (processed DataFrame, handling metadata)
        """
        df = df.copy()
        
        cols_to_drop = [
            col for col, pct in profile['missing_percentage'].items()
            if pct > self.missing_threshold
        ]
        
        if cols_to_drop:
            logger.info(f"Dropping columns with >{self.missing_threshold}% missing: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
            self.columns_dropped.extend(cols_to_drop)
        
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue
            
            col_type = profile['columns'].get(col, 'unknown')
            
            if col_type == 'numerical':
                col_skewness = profile['skewness'].get(col, 0)
                if col_skewness > 1:
                    strategy = 'median'
                    value = df[col].median()
                else:
                    strategy = 'mean'
                    value = df[col].mean()
                
                df[col].fillna(value, inplace=True)
                self.imputation_strategy[col] = {'method': strategy, 'value': value}
                logger.info(f"Imputed {col} using {strategy}: {value:.4f}")
            
            elif col_type == 'categorical':
                value = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df[col].fillna(value, inplace=True)
                self.imputation_strategy[col] = {'method': 'most_frequent', 'value': value}
                logger.info(f"Imputed {col} using most_frequent: {value}")
            
            elif col_type == 'datetime':
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(method='bfill', inplace=True)
                self.imputation_strategy[col] = {'method': 'forward_fill'}
                logger.info(f"Imputed {col} using forward fill")
        
        return df, self.imputation_strategy


class OutlierHandler:
    """Detect and handle outliers using IQR method."""
    
    def __init__(self, method: str = 'cap'):
        """
        Initialize outlier handler.
        
        Args:
            method: 'cap' to cap outliers or 'remove' to remove rows
        """
        self.method = method
        self.bounds = {}
        self.rows_removed = 0
    
    def handle_outliers(
        self, 
        df: pd.DataFrame, 
        profile: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Detect and handle outliers using IQR method.
        
        Args:
            df: Input DataFrame
            profile: Data profile information
            
        Returns:
            Tuple of (processed DataFrame, outlier metadata)
        """
        df = df.copy()
        
        numerical_cols = [
            col for col, col_type in profile['columns'].items()
            if col_type == 'numerical' and col in df.columns
        ]
        
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_count = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            
            if outlier_count > 0:
                self.bounds[col] = {'lower': lower_bound, 'upper': upper_bound}
                
                if self.method == 'cap':
                    df[col] = df[col].clip(lower_bound, upper_bound)
                    logger.info(f"Capped {outlier_count} outliers in {col}")
                elif self.method == 'remove':
                    initial_rows = len(df)
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                    removed = initial_rows - len(df)
                    self.rows_removed += removed
                    logger.info(f"Removed {removed} rows with outliers in {col}")
        
        return df, self.bounds


class DatetimeHandler:
    """Extract features from datetime columns."""
    
    def __init__(self):
        """Initialize datetime handler."""
        self.datetime_columns_dropped = []
    
    def handle_datetime(
        self, 
        df: pd.DataFrame, 
        profile: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Extract features from datetime columns and drop original.
        
        Args:
            df: Input DataFrame
            profile: Data profile information
            
        Returns:
            Tuple of (processed DataFrame, list of extracted features)
        """
        df = df.copy()
        datetime_cols = [
            col for col, col_type in profile['columns'].items()
            if col_type == 'datetime' and col in df.columns
        ]
        
        extracted_features = []
        
        for col in datetime_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            df[f'{col}_year'] = df[col].dt.year
            df[f'{col}_month'] = df[col].dt.month
            df[f'{col}_day'] = df[col].dt.day
            df[f'{col}_dayofweek'] = df[col].dt.dayofweek
            
            extracted_features.extend([
                f'{col}_year', f'{col}_month', 
                f'{col}_day', f'{col}_dayofweek'
            ])
            
            self.datetime_columns_dropped.append(col)
            logger.info(f"Extracted datetime features from {col}")
        
        df = df.drop(columns=datetime_cols)
        
        return df, extracted_features


class CategoricalEncoder:
    """Handle categorical variable encoding."""
    
    def __init__(self, cardinality_threshold: int = 10):
        """
        Initialize categorical encoder.
        
        Args:
            cardinality_threshold: Use OneHot if cardinality <= threshold, else LabelEncode
        """
        self.cardinality_threshold = cardinality_threshold
        self.encoders = {}
        self.onehot_features = []
        self.label_encoded_features = []
    
    def encode_categoricals(
        self, 
        df: pd.DataFrame, 
        profile: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Encode categorical variables intelligently.
        
        Args:
            df: Input DataFrame
            profile: Data profile information
            
        Returns:
            Tuple of (processed DataFrame, encoding metadata)
        """
        df = df.copy()
        
        categorical_cols = [
            col for col, col_type in profile['columns'].items()
            if col_type == 'categorical' and col in df.columns
        ]
        
        for col in categorical_cols:
            cardinality = profile['cardinality'].get(col, 0)
            
            if cardinality <= self.cardinality_threshold:
                df = pd.get_dummies(df, columns=[col], prefix=col, drop_first=False)
                self.onehot_features.extend([c for c in df.columns if c.startswith(f'{col}_')])
                logger.info(f"OneHot encoded {col} (cardinality: {cardinality})")
            else:
                encoder = LabelEncoder()
                df[col] = encoder.fit_transform(df[col].astype(str))
                self.encoders[col] = encoder
                self.label_encoded_features.append(col)
                logger.info(f"Label encoded {col} (cardinality: {cardinality})")
        
        encoding_metadata = {
            'label_encoders': self.encoders,
            'onehot_features': self.onehot_features,
            'label_encoded_features': self.label_encoded_features
        }
        
        return df, encoding_metadata


class NumericalScaler:
    """Scale numerical features based on data distribution."""
    
    def __init__(self):
        """Initialize numerical scaler."""
        self.scalers = {}
        self.scaler_types = {}
    
    def scale_numericals(
        self, 
        df: pd.DataFrame, 
        profile: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Scale numerical features intelligently.
        
        Args:
            df: Input DataFrame
            profile: Data profile information
            
        Returns:
            Tuple of (processed DataFrame, scaler metadata)
        """
        df = df.copy()
        
        numerical_cols = [
            col for col, col_type in profile['columns'].items()
            if col_type == 'numerical' and col in df.columns
        ]
        
        for col in numerical_cols:
            col_skewness = profile['skewness'].get(col, 0)
            
            if col_skewness > 1:
                scaler = RobustScaler()
                scaler_type = 'RobustScaler'
            else:
                scaler = StandardScaler()
                scaler_type = 'StandardScaler'
            
            df[col] = scaler.fit_transform(df[[col]])
            self.scalers[col] = scaler
            self.scaler_types[col] = scaler_type
            logger.info(f"Scaled {col} using {scaler_type}")
        
        scaler_metadata = {
            'scalers': self.scalers,
            'scaler_types': self.scaler_types
        }
        
        return df, scaler_metadata


class FeatureSelector:
    """Remove constant and duplicate columns."""
    
    def __init__(self):
        """Initialize feature selector."""
        self.columns_removed = []
    
    def select_features(
        self, 
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Remove constant and duplicate columns.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (processed DataFrame, list of removed columns)
        """
        df = df.copy()
        
        constant_cols = [col for col in df.columns if df[col].nunique() == 1]
        if constant_cols:
            df = df.drop(columns=constant_cols)
            self.columns_removed.extend(constant_cols)
            logger.info(f"Removed constant columns: {constant_cols}")
        
        duplicate_cols = [col for i, col in enumerate(df.columns) 
                         if col in df.columns[:i]]
        if duplicate_cols:
            df = df.drop(columns=duplicate_cols)
            self.columns_removed.extend(duplicate_cols)
            logger.info(f"Removed duplicate columns: {duplicate_cols}")
        
        return df, self.columns_removed


class AutoPreprocessor:
    """Main preprocessing pipeline orchestrator."""
    
    def __init__(
        self,
        missing_threshold: float = 40.0,
        outlier_method: str = 'cap',
        cardinality_threshold: int = 10
    ):
        """
        Initialize auto preprocessor.
        
        Args:
            missing_threshold: Missing value threshold for column removal
            outlier_method: 'cap' or 'remove'
            cardinality_threshold: Threshold for OneHot vs Label encoding
        """
        self.missing_threshold = missing_threshold
        self.outlier_method = outlier_method
        self.cardinality_threshold = cardinality_threshold
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from CSV or XLSX file.
        
        Args:
            file_path: Path to input file
            
        Returns:
            Loaded DataFrame
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
            logger.info(f"Loaded CSV file: {file_path}")
        elif file_ext == '.xlsx':
            df = pd.read_excel(file_path)
            logger.info(f"Loaded XLSX file: {file_path}")
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        logger.info(f"Data loaded with shape: {df.shape}")
        return df
    
    def preprocess(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
        """
        Execute full preprocessing pipeline.
        
        Args:
            df: Input DataFrame
            target_column: Optional target column name
            
        Returns:
            Tuple of (processed DataFrame, report, metadata)
        """
        original_shape = df.shape
        metadata = {}
        
        profiler = DataProfiler()
        profile = profiler.profile_data(df)
        
        missing_handler = MissingValueHandler(self.missing_threshold)
        df, imputation_meta = missing_handler.handle_missing(df, profile)
        metadata['imputation'] = imputation_meta
        metadata['columns_dropped_missing'] = missing_handler.columns_dropped
        
        outlier_handler = OutlierHandler(self.outlier_method)
        df, outlier_meta = outlier_handler.handle_outliers(df, profile)
        metadata['outliers'] = outlier_meta
        metadata['rows_removed_outliers'] = outlier_handler.rows_removed
        
        datetime_handler = DatetimeHandler()
        df, datetime_features = datetime_handler.handle_datetime(df, profile)
        metadata['datetime_features_extracted'] = datetime_features
        metadata['datetime_columns_dropped'] = datetime_handler.datetime_columns_dropped
        
        categorical_encoder = CategoricalEncoder(self.cardinality_threshold)
        df, encoding_meta = categorical_encoder.encode_categoricals(df, profile)
        metadata['encoding'] = encoding_meta
        
        numerical_scaler = NumericalScaler()
        df, scaler_meta = numerical_scaler.scale_numericals(df, profile)
        metadata['scaling'] = scaler_meta
        
        feature_selector = FeatureSelector()
        df, removed_features = feature_selector.select_features(df)
        metadata['features_removed'] = removed_features
        
        if target_column and target_column in df.columns:
            metadata['target_column'] = target_column
            logger.info(f"Target column identified: {target_column}")
        
        report = {
            'original_shape': original_shape,
            'final_shape': df.shape,
            'rows_removed': original_shape[0] - df.shape[0],
            'columns_removed': original_shape[1] - df.shape[1],
            'profile': profile,
            'preprocessing_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Preprocessing completed. Final shape: {df.shape}")
        
        return df, report, metadata


def auto_preprocess(
    file_path: str,
    target_column: Optional[str] = None,
    save_output: bool = True,
    missing_threshold: float = 40.0,
    outlier_method: str = 'cap',
    cardinality_threshold: int = 10
) -> Dict[str, Any]:
    """
    Automatically preprocess CSV or XLSX file to produce ML-ready dataset.
    
    Args:
        file_path: Path to input CSV or XLSX file
        target_column: Optional target column name
        save_output: Whether to save processed data to CSV
        missing_threshold: Threshold (%) for dropping columns with missing values
        outlier_method: 'cap' to cap outliers or 'remove' to remove rows
        cardinality_threshold: Cardinality threshold for OneHot vs Label encoding
    
    Returns:
        Dictionary containing:
            'data': Processed DataFrame
            'report': Preprocessing report
            'metadata': Preprocessing metadata with encoders and scalers
    """
    logger.info(f"Starting preprocessing for: {file_path}")
    
    preprocessor = AutoPreprocessor(
        missing_threshold=missing_threshold,
        outlier_method=outlier_method,
        cardinality_threshold=cardinality_threshold
    )
    
    df = preprocessor.load_data(file_path)
    processed_df, report, metadata = preprocessor.preprocess(df, target_column)
    
    if save_output:
        output_path = os.path.join(
            os.path.dirname(file_path),
            'processed_data.csv'
        )
        processed_df.to_csv(output_path, index=False)
        logger.info(f"Processed data saved to: {output_path}")
        metadata['output_path'] = output_path
    
    result = {
        'data': processed_df,
        'report': report,
        'metadata': metadata
    }
    
    logger.info("Preprocessing completed successfully")
    
    return result


if __name__ == '__main__':
    pass
