# Quick Setup Guide - File Upload & Preprocessing API

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd d:\SGP\PrepIt-Data preproccesing\PrepIt\backend
pip install -r requirements.txt
```

### Step 2: Configure Supabase

1. **Create Supabase Project:**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Note your project URL and anon key

2. **Update `.env` file:**

```env
# Add these to your existing .env file

# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_BUCKET_ORIGINALS=originals
SUPABASE_BUCKET_PROCESSED=processed

# File Upload Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
```

### Step 3: Create Storage Buckets (Optional)

The API will auto-create buckets, but you can create them manually:

1. Go to Supabase Dashboard → Storage
2. Click "New bucket"
3. Create bucket named: `originals` (set to private)
4. Create bucket named: `processed` (set to private)

### Step 4: Start Server

```bash
uvicorn app.main:app --reload
```

Server starts at: `http://localhost:8000`

### Step 5: Test API

**Visit API Documentation:**
```
http://localhost:8000/docs
```

**Test Health Check:**
```bash
curl http://localhost:8000/health
```

**Test Upload (with authentication):**
```bash
# First login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Use the returned id_token
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@your_data.csv"
```

## 📝 Quick Test Workflow

### 1. Create Test User

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "test123456"
  }'
```

Save the `id_token` from response.

### 2. Upload & Process File

```bash
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer YOUR_ID_TOKEN" \
  -F "file=@dataset.csv" \
  -F "target_column=price" \
  -F "outlier_method=cap"
```

### 3. Download Files

Use the URLs from the response:
- `original_file_url` - Download original file
- `processed_file_url` - Download cleaned, ML-ready file

## 🔍 Verify Setup

### Check All Services

```python
import requests
import os

base_url = "http://localhost:8000"

# 1. Check API health
health = requests.get(f"{base_url}/health")
print("API Health:", health.json())

# 2. Check dataset service
dataset_health = requests.get(f"{base_url}/api/dataset/health")
print("Dataset Service:", dataset_health.json())

# 3. Check Supabase connection
from app.services.storage import get_storage_service

try:
    storage = get_storage_service()
    print("✅ Supabase connected successfully")
except Exception as e:
    print("❌ Supabase error:", e)
```

## ⚙️ Configuration Options

### File Size Limit

Change in `.env`:
```env
MAX_FILE_SIZE_MB=100  # Allow up to 100MB files
```

### Allowed File Types

Change in `.env`:
```env
ALLOWED_EXTENSIONS=csv,xlsx,xls,tsv  # Add more formats
```

### Preprocessing Defaults

Modify in API request:
```python
data = {
    "target_column": "price",
    "missing_threshold": 30.0,      # More aggressive
    "outlier_method": "remove",      # Remove outliers
    "cardinality_threshold": 5,      # More OneHot encoding
    "scaling_method": "minmax"       # Force MinMax scaling
}
```

## 🐛 Common Issues

### "Missing Supabase configuration"

**Problem:** Environment variables not loaded

**Fix:**
```bash
# Verify .env file exists
cat .env | grep SUPABASE

# Restart server
uvicorn app.main:app --reload
```

### "Failed to upload to Supabase"

**Problem:** Invalid credentials or bucket doesn't exist

**Fix:**
1. Check `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Verify buckets exist in Supabase Dashboard
3. Check bucket permissions (should be private)

### "Preprocessing failed"

**Problem:** Invalid data format

**Fix:**
1. Ensure file is valid CSV/Excel
2. Check for corrupted data
3. Review error message in response
4. Check server logs for details

### "File too large"

**Problem:** File exceeds size limit

**Fix:**
```env
MAX_FILE_SIZE_MB=100  # Increase limit
```

### "Authentication failed"

**Problem:** Invalid or expired token

**Fix:**
1. Login again to get fresh token
2. Check token is passed in Authorization header
3. Verify Firebase credentials in `.env`

## 📚 Next Steps

1. **Review API Documentation:**
   - Read [API_UPLOAD_GUIDE.md](API_UPLOAD_GUIDE.md)
   - Explore [http://localhost:8000/docs](http://localhost:8000/docs)

2. **Understand Preprocessing:**
   - Review `preprocessor.py` (read-only)
   - Check preprocessing report in API response

3. **Integrate with Frontend:**
   - Use provided JavaScript/Python examples
   - Handle success/error responses
   - Display preprocessing report to users

4. **Production Deployment:**
   - Update CORS settings in `main.py`
   - Use production Supabase credentials
   - Set up proper logging and monitoring
   - Configure file retention policies

## 🎯 Expected Flow

```
User → Frontend → API → Validate File
                    ↓
                 Upload to Supabase (original)
                    ↓
                 Preprocess (preprocessor.py)
                    ↓
                 Upload to Supabase (processed)
                    ↓
                 Return URLs → Frontend → User
```

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Supabase project created
- [ ] Environment variables configured
- [ ] Server starts without errors
- [ ] Health check passes
- [ ] Can login/signup
- [ ] Can upload file
- [ ] Receives both URLs in response
- [ ] Can download files from URLs
- [ ] Preprocessing report looks correct

---

**Ready to go!** 🚀

For detailed API reference, see [API_UPLOAD_GUIDE.md](API_UPLOAD_GUIDE.md)
