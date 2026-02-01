# Supabase Storage Setup Guide

## Issue
You're getting the following errors:
- `new row violates row-level security policy` (403)
- `Bucket not found` (404)

These occur because:
1. Storage buckets don't exist yet
2. Row-Level Security (RLS) policies are blocking bucket creation/access via API

## Solution: Manual Bucket Setup

### Step 1: Create Storage Buckets

1. **Go to Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard/project/zckkagpbivbjyukgitmi

2. **Open Storage Section**
   - Click on "Storage" in the left sidebar
   - Click "New bucket" button

3. **Create "originals" Bucket**
   - Name: `originals`
   - Public bucket: **UNCHECK** (keep it private)
   - File size limit: 52428800 (50 MB)
   - Allowed MIME types: Leave empty or add:
     ```
     text/csv
     application/vnd.ms-excel
     application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
     ```
   - Click "Create bucket"

4. **Create "processed" Bucket**
   - Name: `processed`
   - Public bucket: **UNCHECK** (keep it private)
   - File size limit: 52428800 (50 MB)
   - Allowed MIME types: Same as above
   - Click "Create bucket"

### Step 2: Configure Row-Level Security Policies

#### For "originals" Bucket:

1. Click on the "originals" bucket
2. Go to "Policies" tab
3. Click "New Policy"
4. Create the following policies:

**Policy 1: Allow Authenticated Uploads**
```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'originals' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

**Policy 2: Allow Users to Read Their Own Files**
```sql
CREATE POLICY "Allow users to read own files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'originals'
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

**Policy 3: Allow Users to Delete Their Own Files**
```sql
CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'originals'
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

#### For "processed" Bucket:

Repeat the same policies for the "processed" bucket (replace `'originals'` with `'processed'`):

```sql
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'processed' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to read own files"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'processed'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to delete own files"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'processed'
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

### Step 3: Alternative - Quick Setup via SQL

If you prefer SQL, go to SQL Editor in Supabase and run:

```sql
-- Enable RLS on storage.objects (should already be enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policies for originals bucket
CREATE POLICY "Allow authenticated uploads to originals"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'originals' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to read own files in originals"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'originals'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to delete own files in originals"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'originals'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

-- Policies for processed bucket
CREATE POLICY "Allow authenticated uploads to processed"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'processed' 
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to read own files in processed"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'processed'
  AND (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Allow users to delete own files in processed"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'processed'
  AND (storage.foldername(name))[1] = auth.uid()::text
);
```

## Explanation of Policies

The policies ensure:
- Only **authenticated users** can upload files
- Files are stored in user-specific folders: `{user_id}/{filename}`
- Users can only access their own files (based on folder structure)
- The `auth.uid()` function ensures user isolation

## Verification

After setup, test by:
1. Restarting your backend server
2. Uploading a file through the API
3. Check Supabase Storage dashboard to see the uploaded file

## Alternative: Use Service Role Key (NOT RECOMMENDED for Production)

If you need to bypass RLS for testing:

1. Get your **service_role** key from Supabase Dashboard (Settings > API)
2. Add to `.env`:
   ```env
   SUPABASE_SERVICE_KEY=your_service_role_key_here
   ```
3. Update `storage.py` to use service key:
   ```python
   self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
   ```

**WARNING**: Service role key bypasses all RLS policies. Only use for development/testing!

## Troubleshooting

### Error: "Bucket not found"
- Ensure buckets are created with exact names: `originals` and `processed`

### Error: "new row violates row-level security policy"
- Ensure RLS policies are created as shown above
- Verify your Firebase auth token is valid and being sent to Supabase

### Error: "Invalid JWT"
- Make sure you're passing the Firebase auth token correctly
- Check that Supabase Auth is configured to accept Firebase tokens (or use Supabase Auth instead)

## Next Steps

1. Complete the bucket setup above
2. Restart your backend: `uvicorn app.main:app --reload`
3. Try uploading a file again
