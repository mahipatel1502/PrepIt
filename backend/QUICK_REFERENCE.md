# 🚀 Quick Reference - File Upload API

## Installation

```bash
pip install -r requirements.txt
```

## Configuration (.env)

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-anon-key

# Optional (have defaults)
SUPABASE_BUCKET_ORIGINALS=originals
SUPABASE_BUCKET_PROCESSED=processed
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
```

## Start Server

```bash
uvicorn app.main:app --reload
```

## API Endpoint

```
POST /api/dataset/upload
```

**Auth:** Required (Bearer token)

## cURL Example

```bash
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@data.csv" \
  -F "target_column=price" \
  -F "outlier_method=cap"
```

## JavaScript Example

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('target_column', 'price');

const response = await fetch('/api/dataset/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

const result = await response.json();
console.log(result.processed_file_url);
```

## Python Example

```python
import requests

files = {'file': open('data.csv', 'rb')}
data = {'target_column': 'price'}
headers = {'Authorization': f'Bearer {token}'}

r = requests.post(
    'http://localhost:8000/api/dataset/upload',
    files=files,
    data=data,
    headers=headers
)

print(r.json()['processed_file_url'])
```

## Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `file` | File | **Required** | .csv, .xlsx, .xls |
| `target_column` | String | None | Column name |
| `missing_threshold` | Float | 50.0 | 0-100 |
| `outlier_method` | String | 'cap' | 'cap', 'remove', 'none' |
| `cardinality_threshold` | Integer | 10 | Any integer |
| `scaling_method` | String | 'auto' | 'auto', 'minmax', 'standard', 'robust' |

## Response

```json
{
  "status": "success",
  "original_file_url": "https://...",
  "processed_file_url": "https://...",
  "preprocessing_report": {
    "original_shape": [1000, 15],
    "final_shape": [980, 45],
    "processing_time_seconds": 3.42
  }
}
```

## Files Created

### New Files
- `app/services/storage.py` - Supabase storage operations
- `app/services/preprocessing_orchestrator.py` - Preprocessing pipeline orchestrator
- `API_UPLOAD_GUIDE.md` - Complete API documentation
- `QUICK_SETUP_UPLOAD.md` - Setup guide
- `IMPLEMENTATION_COMPLETE.md` - Implementation summary

### Modified Files
- `app/routes/dataset.py` - New upload endpoint
- `app/utils/file_handler.py` - Enhanced validation
- `app/main.py` - Updated with logging
- `requirements.txt` - Added supabase, scipy, python-magic-bin
- `.env` - Added Supabase configuration
- `.env.example` - Updated template

### Unchanged
- `preprocessor.py` - ✅ **NOT MODIFIED** (black box)

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Dataset service health
curl http://localhost:8000/api/dataset/health
```

## Common Issues

### Missing Supabase config
→ Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`

### Upload failed
→ Check Supabase credentials and bucket permissions

### File too large
→ Increase `MAX_FILE_SIZE_MB` in `.env`

### Authentication failed
→ Login again to get fresh ID token

## Testing

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# 3. Upload file
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer TOKEN_FROM_STEP_2" \
  -F "file=@test.csv"
```

## Documentation

- **Full API Guide:** [API_UPLOAD_GUIDE.md](API_UPLOAD_GUIDE.md)
- **Setup Guide:** [QUICK_SETUP_UPLOAD.md](QUICK_SETUP_UPLOAD.md)
- **Implementation:** [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
- **Interactive Docs:** http://localhost:8000/docs

## Architecture

```
File Upload → Validate → Store Original (Supabase)
                ↓
           Preprocess (preprocessor.py)
                ↓
         Store Processed (Supabase)
                ↓
          Return Both URLs
```

## Security

✅ File validation (type, size, integrity)  
✅ Filename sanitization  
✅ Authentication required  
✅ Private storage buckets  
✅ Signed URLs (24h expiration)  
✅ Temp file cleanup  

---

**Ready!** Start server and test at http://localhost:8000/docs
