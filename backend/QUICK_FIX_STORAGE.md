# Quick Fix for Supabase Storage Errors

## Your Error
```
Bucket not found
new row violates row-level security policy
```

## Root Cause
The Supabase storage buckets (`originals` and `processed`) don't exist yet, and RLS policies prevent creating them via API.

## Quick Solution (Choose One)

### Option A: Manual Setup (RECOMMENDED for Production) ⭐

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard/project/zckkagpbivbjyukgitmi

2. **Create Buckets**:
   - Click "Storage" → "New bucket"
   - Create bucket named: `originals` (uncheck "Public bucket")
   - Create bucket named: `processed` (uncheck "Public bucket")

3. **Add RLS Policies** (SQL Editor):
   ```sql
   -- For originals bucket
   CREATE POLICY "Allow authenticated uploads to originals"
   ON storage.objects FOR INSERT TO authenticated
   WITH CHECK (bucket_id = 'originals' AND (storage.foldername(name))[1] = auth.uid()::text);

   CREATE POLICY "Allow users to read own files in originals"
   ON storage.objects FOR SELECT TO authenticated
   USING (bucket_id = 'originals' AND (storage.foldername(name))[1] = auth.uid()::text);

   -- For processed bucket
   CREATE POLICY "Allow authenticated uploads to processed"
   ON storage.objects FOR INSERT TO authenticated
   WITH CHECK (bucket_id = 'processed' AND (storage.foldername(name))[1] = auth.uid()::text);

   CREATE POLICY "Allow users to read own files in processed"
   ON storage.objects FOR SELECT TO authenticated
   USING (bucket_id = 'processed' AND (storage.foldername(name))[1] = auth.uid()::text);
   ```

4. **Restart Backend**:
   ```bash
   # Stop current server (Ctrl+C)
   uvicorn app.main:app --reload
   ```

### Option B: Use Service Role Key (ONLY for Development/Testing) ⚠️

1. **Get Service Role Key**:
   - Supabase Dashboard → Settings → API
   - Copy the `service_role` key (NOT the anon key)

2. **Add to .env**:
   ```env
   SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.your_service_key_here...
   ```

3. **Still need to create buckets manually** (Step 2 from Option A)

4. **Restart Backend**

**⚠️ WARNING**: Service role key bypasses ALL security. Never use in production!

## Verify Setup

Run this test script:
```bash
python test_storage_config.py
```

## Full Documentation

See [SUPABASE_STORAGE_SETUP.md](./SUPABASE_STORAGE_SETUP.md) for complete setup instructions.

## Still Having Issues?

Check:
1. ✓ Buckets created with exact names: `originals` and `processed`
2. ✓ RLS policies added
3. ✓ Backend restarted
4. ✓ Valid auth token being sent with requests
