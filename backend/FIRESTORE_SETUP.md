# Firestore Database Setup Guide

## The Issue
You're seeing this error:
```
google.api_core.exceptions.NotFound: 404 The database (default) does not exist for project prepit-200
```

This means your Firebase project exists, but **Firestore Database hasn't been created yet**.

## Quick Fix (5 minutes)

### Step 1: Go to Firebase Console
1. Open [Firebase Console](https://console.firebase.google.com)
2. Select your project: **prepit-200**

### Step 2: Create Firestore Database
1. Click **"Firestore Database"** in the left sidebar (under "Build" section)
2. Click **"Create database"** button
3. Choose a mode:
   - **Test mode** - For development (allows all read/write for 30 days)
   - **Production mode** - For production (requires authentication rules)
   
   💡 **Recommendation:** Use Test mode for now

4. Select your region (choose closest to you, e.g., `us-central` or `europe-west`)
5. Click **"Enable"**
6. Wait 1-2 minutes for database creation

### Step 3: Restart Backend
Once the database is created:
```bash
# Stop the current uvicorn server (Ctrl+C)
# Then restart:
uvicorn app.main:app --reload
```

### Step 4: Test Authentication
Your auth endpoints should now work:
- POST `/api/auth/signup` - Create new user
- POST `/api/auth/login` - Login with credentials

## Security Rules for Development

If you chose Test mode, your rules are already set. If you chose Production mode, update rules:

1. Go to Firebase Console → Firestore Database → Rules
2. Replace with these **development-only** rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow authenticated users to read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Allow all for development (REMOVE IN PRODUCTION!)
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click **"Publish"**

⚠️ **IMPORTANT:** These rules allow anyone to read/write. Use only for development!

## Production Security Rules

For production, use these secure rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users collection - only allow users to read/update their own profile
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow update: if request.auth != null && request.auth.uid == userId;
      allow create, delete: if false;
    }
    
    // Deny all other access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

## Verify Setup

Test the backend:
```bash
# Health check
curl http://localhost:8000/health

# Signup test
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"Test1234"}'
```

## Troubleshooting

### Error: "Permission denied"
- Check your Firestore rules
- Ensure Test mode is enabled OR update rules

### Error: "Firebase credentials not found"
- Check `.env` file has correct `FIREBASE_CREDENTIALS_PATH`
- Verify `firebase-credentials.json` exists

### Error: "Invalid project ID"
- Open `firebase-credentials.json`
- Verify `project_id` matches your Firebase project

## Collection Structure

Once set up, Firestore will have this structure:
```
prepit-200 (database)
└── users (collection)
    ├── user_doc_1
    │   ├── email: "user@example.com"
    │   ├── full_name: "User Name"
    │   ├── password_hash: "$2b$12..."
    │   ├── created_at: "2026-02-01T..."
    │   └── updated_at: "2026-02-01T..."
    └── user_doc_2
        └── ...
```

## Next Steps

After database is created:
1. ✅ Test signup endpoint
2. ✅ Test login endpoint  
3. ✅ Verify JWT tokens are working
4. ✅ Update security rules for production
5. ✅ Set up indexes if needed (for complex queries)

---

**Need Help?** Check Firebase Console → Firestore Database → Usage tab to monitor database activity.
