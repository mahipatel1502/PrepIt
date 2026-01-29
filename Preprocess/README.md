# Data Preprocessing Module

A universal, production-grade data preprocessing pipeline that intelligently handles all types of datasets (time-series, categorical, numerical, mixed) for machine learning.

## Features

✅ **Universal Data Handling**
- Supports CSV and Excel (XLSX/XLS) files
- Auto-detects column types (numerical, categorical, datetime, boolean, IDs)
- Intelligent type conversion

✅ **Smart Missing Value Handling**
- Drops columns with excessive missing values
- Group-wise forward fill for time-series
- Derives missing values from relationships (e.g., total = sum of parts)
- Type-appropriate imputation (median/mode)

✅ **Data Quality**
- Duplicate removal (time-series aware)
- Outlier detection and handling (IQR method)
- Logical validation (e.g., parts ≤ total, non-negative counts)

✅ **Feature Engineering**
- Datetime feature extraction (year, month, day, quarter, week, etc.)
- Rate features (e.g., positivity_rate = positive/total)
- Trend features (daily changes, 7-day rolling averages)

✅ **Encoding & Scaling**
- Smart categorical encoding (OneHot for low cardinality, Label for high)
- Auto-detects best scaling method (Standard/Robust/MinMax)
- Preserves important columns (IDs, rates, date parts)

✅ **Production Ready**
- Comprehensive logging
- Detailed statistics report
- Error handling
- Both CLI and API interfaces

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Command Line

```bash
# Basic usage
python preprocessor.py data.csv

# With target column
python preprocessor.py data.csv target_column_name

# From any directory
python /path/to/preprocessor.py /path/to/data.xlsx
```

### 2. Python Script

```python
from preprocessor import preprocess_file

# Simple usage
result = preprocess_file('data.csv')
print(result['report'])

# Advanced configuration
result = preprocess_file(
    file_path='data.xlsx',
    target_column='target',
    missing_threshold=50.0,      # Drop columns with >50% missing
    outlier_method='cap',         # 'cap', 'remove', or 'none'
    cardinality_threshold=10,     # OneHot if ≤10 unique values
    scaling_method='auto',        # 'auto', 'minmax', 'standard', 'robust'
    save_output=True,
    output_path='custom_output.csv'
)

# Access processed data
df = result['data']
report = result['report']
```

### 3. FastAPI Backend

```bash
# Start the API server
python api.py

# API will be available at: http://localhost:8000
# Interactive docs at: http://localhost:8000/docs
```

**API Endpoints:**

- `POST /api/preprocess-file-path` - Process file from path
- `POST /api/preprocess-upload` - Upload and process file
- `GET /api/download/{filename}` - Download processed file
- `GET /api/list-processed` - List all processed files

**Example API Call:**

```python
import requests

# Process file from path
response = requests.post('http://localhost:8000/api/preprocess-file-path', json={
    'file_path': 'data.csv',
    'target_column': 'target',
    'missing_threshold': 50.0,
    'outlier_method': 'cap'
})

result = response.json()
print(result['report'])
```

## Configuration Options

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `missing_threshold` | 50.0 | 0-100 | Drop columns with missing % above this |
| `outlier_method` | 'cap' | 'cap', 'remove', 'none' | How to handle outliers |
| `cardinality_threshold` | 10 | Any integer | OneHot if unique values ≤ this |
| `scaling_method` | 'auto' | 'auto', 'minmax', 'standard', 'robust' | Feature scaling method |

## Output

Processed files are saved to the `processed/` directory with format:
```
processed/cleaned_<timestamp>_<original_filename>.csv
```

### Report Structure

```python
{
    'original_shape': (1000, 20),
    'final_shape': (950, 35),
    'rows_removed': 50,
    'columns_added': 15,
    'duplicates_removed': 10,
    'features_engineered': 15,
    'processing_time_seconds': 2.34,
    'column_types': {...},
    'final_columns': [...],
    'dropped_columns': [...],
    'output_path': 'processed/cleaned_20260128_123456_data.csv'
}
```

## Examples

### Example 1: Time-Series Data (COVID, Sales, etc.)

```python
result = preprocess_file('covid_data.csv')
# Auto-detects dates, creates trends, rates, rolling averages
```

### Example 2: General ML Dataset

```python
result = preprocess_file(
    'customer_data.xlsx',
    target_column='churn',
    outlier_method='remove',
    scaling_method='standard'
)
```

### Example 3: High-Cardinality Data

```python
result = preprocess_file(
    'product_catalog.csv',
    cardinality_threshold=20,  # Use label encoding for >20 categories
    missing_threshold=30.0
)
```

## File Structure

```
Preprocess/
├── preprocessor.py          # Main preprocessing module
├── api.py                   # FastAPI backend (optional)
├── requirements.txt         # Dependencies
├── README.md               # This file
├── StatewiseTestingDetails.csv  # Sample data
└── processed/              # Output directory
```

## Key Improvements Over Previous Versions

1. **Universal Compatibility** - Works with any dataset type
2. **Better Error Handling** - Comprehensive validation and logging
3. **Modular Design** - Clean OOP architecture
4. **Smart Defaults** - Auto-detects best preprocessing strategies
5. **Production Ready** - Complete API, logging, and documentation
6. **No Redundancy** - Single, well-tested preprocessing pipeline

## Requirements

- Python 3.8+
- pandas ≥ 2.0.0
- numpy ≥ 1.24.0
- scikit-learn ≥ 1.3.0
- scipy ≥ 1.10.0

## License

MIT License
