# PrepIt Backend API - File Upload & Preprocessing

## Overview

The PrepIt backend provides a complete file preprocessing pipeline that:
- Accepts CSV/Excel files via API
- Stores original files in Supabase storage
- Preprocesses data using the robust `preprocessor.py` pipeline
- Stores processed files in Supabase storage
- Returns downloadable links for both original and processed files

## Architecture

```
Frontend Upload
      ↓
  API Endpoint (/api/dataset/upload)
      ↓
  ┌─────────────────────────────────┐
  │  1. Validate File               │
  │  2. Upload Original → Supabase  │
  │  3. Preprocess (preprocessor.py)│
  │  4. Upload Processed → Supabase │
  │  5. Return URLs                 │
  └─────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET_ORIGINALS=originals
SUPABASE_BUCKET_PROCESSED=processed

# File Upload Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
```

### 3. Setup Supabase Buckets

The system will auto-create buckets, but you can manually create them:

1. Go to Supabase Dashboard → Storage
2. Create bucket: `originals` (private)
3. Create bucket: `processed` (private)

### 4. Start Server

```bash
uvicorn app.main:app --reload
```

Server runs at: `http://localhost:8000`

## API Endpoints

### Upload & Preprocess Dataset

**Endpoint:** `POST /api/dataset/upload`

**Authentication:** Required (Bearer token)

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | File | Yes | - | CSV or Excel file to process |
| `target_column` | String | No | None | Target column name (preserved in output) |
| `missing_threshold` | Float | No | 50.0 | Drop columns with missing % above this |
| `outlier_method` | String | No | 'cap' | Outlier handling: 'cap', 'remove', 'none' |
| `cardinality_threshold` | Integer | No | 10 | Threshold for OneHot vs Label encoding |
| `scaling_method` | String | No | 'auto' | Scaling: 'auto', 'minmax', 'standard', 'robust' |

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@dataset.csv" \
  -F "target_column=price" \
  -F "missing_threshold=50.0" \
  -F "outlier_method=cap" \
  -F "scaling_method=auto"
```

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/api/dataset/upload"
headers = {"Authorization": f"Bearer {id_token}"}

files = {"file": open("dataset.csv", "rb")}
data = {
    "target_column": "price",
    "missing_threshold": 50.0,
    "outlier_method": "cap",
    "scaling_method": "auto"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

**Example Request (JavaScript):**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('target_column', 'price');
formData.append('missing_threshold', '50.0');
formData.append('outlier_method', 'cap');
formData.append('scaling_method', 'auto');

const response = await fetch('http://localhost:8000/api/dataset/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${idToken}`
  },
  body: formData
});

const result = await response.json();
console.log(result);
```

**Success Response (200 OK):**

```json
{
  "status": "success",
  "original_file_url": "https://supabase.co/storage/v1/object/sign/originals/user123/abc123_original_20260201_120000_data.csv?token=...",
  "processed_file_url": "https://supabase.co/storage/v1/object/sign/processed/user123/abc123_processed_20260201_120030_data.csv?token=...",
  "preprocessing_report": {
    "original_shape": [1000, 15],
    "final_shape": [980, 45],
    "rows_removed": 20,
    "columns_added": 30,
    "duplicates_removed": 10,
    "features_engineered": 15,
    "non_informative_columns_removed": ["name", "email"],
    "processing_time_seconds": 3.42,
    "column_types": {
      "datetime": 1,
      "categorical": 3,
      "numerical": 8,
      "count": 3
    },
    "final_columns": ["age", "income_scaled", "category_encoded", ...],
    "dropped_columns": ["name", "email", "phone"],
    "timestamp": "2026-02-01T12:00:30.123456"
  },
  "message": "File processed successfully"
}
```

**Error Response - Preprocessing Failed:**

```json
{
  "status": "error",
  "error_code": "PREPROCESSING_FAILED",
  "message": "Preprocessing failed: Invalid data format in column 'age'",
  "original_file_url": "https://...",
  "processed_file_url": null,
  "preprocessing_report": null
}
```

**Error Response - Validation Failed:**

```json
{
  "detail": "Invalid file type. Allowed: csv, xlsx, xls"
}
```

### Health Check

**Endpoint:** `GET /api/dataset/health`

**Authentication:** Not required

**Response:**

```json
{
  "status": "healthy",
  "service": "dataset-preprocessing",
  "version": "2.0.0"
}
```

## File Storage Structure

### Supabase Storage Organization

```
originals/
  └── user123/
      ├── abc123_original_20260201_120000_sales_data.csv
      ├── def456_original_20260201_140000_customer_data.xlsx
      └── ...

processed/
  └── user123/
      ├── abc123_processed_20260201_120030_sales_data.csv
      ├── def456_processed_20260201_140045_customer_data.csv
      └── ...
```

### File Naming Convention

**Original Files:**
```
{file_id}_original_{timestamp}_{sanitized_filename}
```

**Processed Files:**
```
{file_id}_processed_{timestamp}_{sanitized_filename}
```

## Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `VALIDATION_ERROR` | Invalid file type or size | Check file format and size limits |
| `UPLOAD_FAILED` | Failed to upload original file | Check Supabase configuration |
| `PREPROCESSING_FAILED` | Preprocessing pipeline error | Check data format and quality |
| `PROCESSED_UPLOAD_FAILED` | Failed to upload processed file | Check Supabase storage quota |

## Security Features

### File Validation
- ✅ Filename sanitization (prevent path traversal)
- ✅ File size limits (configurable)
- ✅ File type validation (extension + MIME type)
- ✅ Empty file detection

### Storage Security
- ✅ Private buckets (signed URLs with expiration)
- ✅ User-based folder isolation
- ✅ Unique file identifiers (UUID)
- ✅ Temporary file cleanup

### Authentication
- ✅ Firebase ID token verification
- ✅ User context preserved throughout pipeline
- ✅ Authorization on all endpoints

## Preprocessing Pipeline

The backend uses `preprocessor.py` as a **black box**. It handles:

1. **Data Loading** - CSV/Excel parsing
2. **Column Standardization** - Naming conventions
3. **Type Detection** - Auto-detect datetime, categorical, numerical
4. **Duplicate Removal** - Row deduplication
5. **Missing Value Handling** - Smart imputation strategies
6. **Outlier Detection** - IQR-based capping/removal
7. **Data Validation** - Logical constraint checks
8. **Feature Engineering** - Rate calculations, rolling averages
9. **Datetime Extraction** - Year, month, day features
10. **Categorical Encoding** - OneHot or Label encoding
11. **Feature Scaling** - StandardScaler, MinMaxScaler, RobustScaler
12. **Constant Removal** - Drop constant/duplicate columns

**Output:** ML-ready CSV file with cleaned, scaled, and encoded features

## Configuration Options

### Preprocessing Parameters

#### `missing_threshold` (default: 50.0)
Columns with missing values above this percentage will be dropped.
- **Range:** 0-100
- **Example:** 50.0 = drop columns with >50% missing values

#### `outlier_method` (default: 'cap')
How to handle outliers in numerical columns.
- **Options:**
  - `'cap'` - Cap values at IQR bounds (recommended)
  - `'remove'` - Remove rows with outliers
  - `'none'` - Keep outliers as-is

#### `cardinality_threshold` (default: 10)
Threshold for encoding strategy.
- **Low cardinality (≤ threshold):** OneHot encoding
- **High cardinality (> threshold):** Label encoding
- **Example:** 10 = OneHot for ≤10 unique values

#### `scaling_method` (default: 'auto')
Feature scaling strategy.
- **Options:**
  - `'auto'` - Choose based on data distribution (recommended)
  - `'standard'` - StandardScaler (z-score normalization)
  - `'minmax'` - MinMaxScaler (0-1 range)
  - `'robust'` - RobustScaler (median/IQR, robust to outliers)

## Performance Considerations

### File Size Limits
- Default: 50 MB
- Configurable via `MAX_FILE_SIZE_MB`
- Large files may take longer to process

### Processing Time
- Small files (<1MB): 1-3 seconds
- Medium files (1-10MB): 3-15 seconds
- Large files (10-50MB): 15-60 seconds

### Storage Quotas
- Check Supabase plan limits
- Monitor bucket usage
- Implement cleanup policies for old files

## Monitoring & Logging

All operations are logged with:
- Timestamp
- User ID
- File information
- Processing steps
- Errors and warnings

**Log Levels:**
- `INFO` - Normal operations
- `WARNING` - Non-critical issues
- `ERROR` - Failed operations

## Testing

### Test File Upload

```bash
# Health check
curl http://localhost:8000/api/dataset/health

# Upload test file
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_data.csv"
```

### Test Authentication

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Use returned id_token in upload request
```

## Troubleshooting

### "Missing Supabase configuration"
**Fix:** Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`

### "Failed to upload original file"
**Fix:** Check Supabase credentials and bucket permissions

### "Preprocessing failed"
**Fix:** Check data quality and format. Review preprocessing logs.

### "File too large"
**Fix:** Increase `MAX_FILE_SIZE_MB` or reduce file size

### "Invalid file type"
**Fix:** Ensure file is CSV or Excel format

## API Versioning

Current version: **2.0.0**

Changes in 2.0.0:
- ✅ Supabase storage integration
- ✅ Complete preprocessing pipeline
- ✅ Enhanced file validation
- ✅ Signed URL generation
- ✅ Comprehensive error handling

---

**For more information:**
- API Documentation: http://localhost:8000/docs
- Preprocessing Details: See `preprocessor.py`
- Firebase Auth: See `FIREBASE_AUTH_QUICKREF.md`
