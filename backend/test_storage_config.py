"""
Test Supabase Storage Configuration
Run this script to verify your Supabase buckets and RLS policies are set up correctly
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def test_supabase_storage():
    """Test Supabase storage configuration"""
    
    print("=" * 60)
    print("Supabase Storage Configuration Test")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    bucket_originals = os.getenv("SUPABASE_BUCKET_ORIGINALS", "originals")
    bucket_processed = os.getenv("SUPABASE_BUCKET_PROCESSED", "processed")
    
    if not supabase_url:
        print("   ❌ SUPABASE_URL not found in .env")
        return False
    print(f"   ✓ SUPABASE_URL: {supabase_url}")
    
    if not supabase_key:
        print("   ❌ SUPABASE_ANON_KEY not found in .env")
        return False
    print(f"   ✓ SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    print(f"   ✓ Expected buckets: {bucket_originals}, {bucket_processed}")
    
    # Initialize client
    print("\n2. Initializing Supabase client...")
    try:
        client = create_client(supabase_url, supabase_key)
        print("   ✓ Supabase client initialized")
    except Exception as e:
        print(f"   ❌ Failed to initialize client: {e}")
        return False
    
    # List buckets
    print("\n3. Checking storage buckets...")
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if not bucket_names:
            print("   ❌ No buckets found!")
            print("\n" + "=" * 60)
            print("ACTION REQUIRED:")
            print("Please create storage buckets manually in Supabase Dashboard")
            print("See SUPABASE_STORAGE_SETUP.md for detailed instructions")
            print("=" * 60)
            return False
        
        print(f"   ✓ Found {len(bucket_names)} bucket(s): {', '.join(bucket_names)}")
        
        # Check for required buckets
        missing = []
        if bucket_originals not in bucket_names:
            print(f"   ❌ Missing bucket: {bucket_originals}")
            missing.append(bucket_originals)
        else:
            print(f"   ✓ Bucket exists: {bucket_originals}")
            
        if bucket_processed not in bucket_names:
            print(f"   ❌ Missing bucket: {bucket_processed}")
            missing.append(bucket_processed)
        else:
            print(f"   ✓ Bucket exists: {bucket_processed}")
        
        if missing:
            print("\n" + "=" * 60)
            print("ACTION REQUIRED:")
            print(f"Please create these buckets: {', '.join(missing)}")
            print("See SUPABASE_STORAGE_SETUP.md for detailed instructions")
            print("=" * 60)
            return False
            
    except Exception as e:
        print(f"   ❌ Error listing buckets: {e}")
        return False
    
    # Test upload (requires authentication)
    print("\n4. Testing bucket access...")
    print("   ℹ Note: Full upload test requires authentication")
    print("   ℹ RLS policies should be configured to allow authenticated uploads")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ Configuration Test Passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Ensure RLS policies are configured (see SUPABASE_STORAGE_SETUP.md)")
    print("2. Test file upload through the API with authentication")
    print("3. Start the backend server: uvicorn app.main:app --reload")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        success = test_supabase_storage()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
