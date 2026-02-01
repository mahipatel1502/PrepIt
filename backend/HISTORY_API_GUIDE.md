# User History Module - API Documentation

## Overview

The User History module tracks all preprocessing jobs performed by users, storing metadata in Firestore and linking to files in Supabase Storage. Each user can view, audit, and manage their preprocessing history.

## Architecture

```
User Uploads File
       ↓
Processing Pipeline
       ↓
    Success? ──→ YES ──→ Save History (status: success)
       │                      ↓
       │            Store: original + processed URLs
       │
       NO ──→ Save History (status: failed)
                    ↓
          Store: original URL only
```

### Data Storage

- **Firestore**: Metadata only (history records)
- **Supabase**: Actual file storage (original + processed)
- **Security**: User-scoped access (user can only access their own records)

## History Record Structure

```json
{
  "history_id": "auto_generated_firestore_id",
  "user_id": "firebase_user_uuid",
  "file_id": "uuid_v4",
  "original_file": {
    "file_name": "sales_data.csv",
    "bucket_path": "user123/abc-123_original_20260201_120000_sales_data.csv",
    "file_url": "https://supabase.co/storage/v1/object/sign/originals/..."
  },
  "processed_file": {
    "file_name": "sales_data_processed.csv",
    "bucket_path": "user123/abc-123_processed_20260201_120030_sales_data.csv",
    "file_url": "https://supabase.co/storage/v1/object/sign/processed/..."
  },
  "file_type": "csv",
  "status": "success",
  "created_at": "2026-02-01T12:00:30.123Z",
  "preprocessing_version": "v2.0",
  "preprocessing_report": {
    "original_shape": [1000, 15],
    "final_shape": [980, 45],
    "processing_time_seconds": 3.42,
    ...
  }
}
```

## API Endpoints

### 1. Get User History (List)

**Endpoint:** `GET /api/history`

**Authorization:** Bearer token (required)

**Query Parameters:**
- `limit` (optional): Number of records (1-100, default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "total_count": 25,
  "returned_count": 10,
  "data": [
    {
      "history_id": "abc123def456",
      "original_file_name": "sales_data.csv",
      "processed_file_name": "sales_data_processed.csv",
      "file_type": "csv",
      "status": "success",
      "created_at": "2026-02-01T12:00:30.123Z"
    },
    ...
  ]
}
```

### 2. Get History Detail

**Endpoint:** `GET /api/history/{history_id}`

**Authorization:** Bearer token (required)

**Path Parameters:**
- `history_id`: Unique history record identifier

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/history/abc123def456" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "history_id": "abc123def456",
    "user_id": "user_uuid_123",
    "file_id": "file_uuid_456",
    "original_file": {
      "file_name": "sales_data.csv",
      "bucket_path": "user123/abc-123_original_...",
      "file_url": "https://supabase.co/storage/..."
    },
    "processed_file": {
      "file_name": "sales_data_processed.csv",
      "bucket_path": "user123/abc-123_processed_...",
      "file_url": "https://supabase.co/storage/..."
    },
    "file_type": "csv",
    "status": "success",
    "created_at": "2026-02-01T12:00:30.123Z",
    "preprocessing_version": "v2.0",
    "preprocessing_report": {
      "original_shape": [1000, 15],
      "final_shape": [980, 45],
      "rows_removed": 20,
      "features_engineered": 15,
      "processing_time_seconds": 3.42
    }
  }
}
```

### 3. Delete History

**Endpoint:** `DELETE /api/history/{history_id}`

**Authorization:** Bearer token (required)

**Path Parameters:**
- `history_id`: Unique history record identifier

**Query Parameters:**
- `delete_files` (optional): Also delete files from storage (default: true)

**Example Request:**
```bash
# Delete history + files
curl -X DELETE "http://localhost:8000/api/history/abc123def456?delete_files=true" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"

# Delete history only (keep files)
curl -X DELETE "http://localhost:8000/api/history/abc123def456?delete_files=false" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "message": "History record abc123def456 deleted successfully",
  "deleted_files": {
    "original_deleted": true,
    "processed_deleted": true
  }
}
```

### 4. Get History Statistics

**Endpoint:** `GET /api/history/stats/summary`

**Authorization:** Bearer token (required)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/history/stats/summary" \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "total_records": 25,
    "successful_processings": 23,
    "failed_processings": 2,
    "success_rate": 92.0,
    "recent_activity": [
      {
        "history_id": "abc123",
        "file_name": "sales_data.csv",
        "status": "success",
        "created_at": "2026-02-01T12:00:30.123Z"
      },
      ...
    ]
  }
}
```

## Frontend Integration

### List History Page

```javascript
// Fetch user history
const fetchHistory = async (page = 0, pageSize = 10) => {
  const response = await fetch(
    `${API_URL}/api/history?limit=${pageSize}&offset=${page * pageSize}`,
    {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    }
  );
  
  const data = await response.json();
  return data;
};

// Display in table
data.data.forEach(record => {
  console.log(record.original_file_name, record.status, record.created_at);
});
```

### Download Files

```javascript
// Get full details with file URLs
const getHistoryDetail = async (historyId) => {
  const response = await fetch(
    `${API_URL}/api/history/${historyId}`,
    {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    }
  );
  
  const data = await response.json();
  
  // Download original file
  window.open(data.data.original_file.file_url, '_blank');
  
  // Download processed file
  if (data.data.processed_file) {
    window.open(data.data.processed_file.file_url, '_blank');
  }
};
```

### Delete History

```javascript
const deleteHistory = async (historyId, deleteFiles = true) => {
  const response = await fetch(
    `${API_URL}/api/history/${historyId}?delete_files=${deleteFiles}`,
    {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    }
  );
  
  const data = await response.json();
  console.log(data.message);
};
```

## Security Rules

### Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /preprocessing_history/{document=**} {
      // Users can only read their own history
      allow read: if request.auth != null 
                  && resource.data.user_id == request.auth.uid;
      
      // Users can only create with their own user_id
      allow create: if request.auth != null 
                    && request.resource.data.user_id == request.auth.uid;
      
      // Users can only delete their own history
      allow delete: if request.auth != null 
                    && resource.data.user_id == request.auth.uid;
      
      // No updates allowed (immutable history)
      allow update: if false;
    }
  }
}
```

### Backend Verification

All endpoints verify:
1. ✅ User is authenticated (Firebase token)
2. ✅ `user_id` from token matches record owner
3. ✅ Never trust `user_id` from request body

## When History is Created

### Success Case
1. File uploaded ✅
2. Preprocessing succeeds ✅
3. Processed file uploaded ✅
4. **History created** with status="success"

### Partial Failure
1. File uploaded ✅
2. Preprocessing fails ❌
3. **History created** with status="failed", no processed file info

### Complete Failure
1. File upload fails ❌
2. **No history created** (nothing to track)

## History Data Flow

```
Upload Endpoint (/api/dataset/upload)
       ↓
   [File uploaded to Supabase]
       ↓
   [Preprocessing runs]
       ↓
   Success? ──YES──→ [Processed file uploaded]
       │                      ↓
       │              [Create history: success]
       │
       NO ──→ [Create history: failed]
       
Both paths save history record in Firestore
```

## Error Handling

### History Creation Fails
- Upload and processing continue
- Error logged but not returned to user
- System remains functional

### History Fetch Fails
- Return 500 error with details
- Frontend should show error message

### History Delete Fails
- If Firestore delete fails: Return error
- If file delete fails: Continue with history delete
- Status returned for each operation

## Pagination

### Example: Get Page 2 (items 10-19)
```bash
curl "http://localhost:8000/api/history?limit=10&offset=10"
```

### Calculate Pages
```javascript
const totalPages = Math.ceil(totalCount / pageSize);
const currentPage = Math.floor(offset / pageSize) + 1;
```

## Testing

### Test History Creation
```bash
# 1. Upload a file
curl -X POST "http://localhost:8000/api/dataset/upload" \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test.csv"

# 2. Check history was created
curl "http://localhost:8000/api/history" \
  -H "Authorization: Bearer TOKEN"
```

### Test History Retrieval
```bash
# Get history list
curl "http://localhost:8000/api/history?limit=5" \
  -H "Authorization: Bearer TOKEN"

# Get specific record (use history_id from above)
curl "http://localhost:8000/api/history/abc123def456" \
  -H "Authorization: Bearer TOKEN"
```

### Test History Deletion
```bash
# Delete with files
curl -X DELETE "http://localhost:8000/api/history/abc123def456" \
  -H "Authorization: Bearer TOKEN"
```

## Performance Considerations

### Firestore Limits
- Max 1 write/second per document
- Queries automatically indexed
- Pagination recommended for large datasets

### Storage Cleanup
- Signed URLs expire after 24 hours
- Consider implementing file retention policy
- Delete old files to save storage costs

## Monitoring

### Key Metrics
- History records created per day
- Failed preprocessing rate
- Average file sizes
- Storage usage per user

### Logging
All operations logged with:
- User ID
- History ID
- Action performed
- Success/failure status

---

**For complete API documentation, visit:** http://localhost:8000/docs
