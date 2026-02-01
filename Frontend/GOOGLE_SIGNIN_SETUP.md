# Google Sign-In Setup Guide

This guide will help you set up Google authentication using Firebase in the PrepIt frontend.

## ✅ What's Been Implemented

The Google sign-in functionality has been fully implemented in the frontend with the following components:

1. **Firebase Integration** ([lib/firebase.ts](lib/firebase.ts))
   - Firebase initialization
   - Google authentication provider setup
   - Sign-in with popup functionality
   - ID token retrieval
   - Error handling for common scenarios

2. **Auth Context** ([context/auth-context.tsx](context/auth-context.tsx))
   - `loginWithGoogle()` method implemented
   - Integrates Firebase with backend API
   - Manages user state after Google sign-in

3. **API Client** ([lib/api-client.ts](lib/api-client.ts))
   - `loginWithGoogle()` endpoint added
   - Sends Firebase ID token to backend for verification

4. **UI Components**
   - Login page ([app/login/page.tsx](app/login/page.tsx)) with Google button
   - Signup page ([app/signup/page.tsx](app/signup/page.tsx)) with Google button
   - Both pages already have the "Continue with Google" button

## 🔧 Setup Instructions

### Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard to create your project

### Step 2: Enable Google Authentication

1. In your Firebase project, go to **Build** → **Authentication**
2. Click **Get Started** (if first time)
3. Go to **Sign-in method** tab
4. Click on **Google** provider
5. Toggle **Enable**
6. Add a support email (required)
7. Click **Save**

### Step 3: Register Your Web App

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Scroll down to **Your apps** section
3. Click the **Web** icon (`</>`)
4. Register your app:
   - **App nickname**: PrepIt (or any name you prefer)
   - **Firebase Hosting**: Leave unchecked for now
5. Click **Register app**
6. Copy the `firebaseConfig` object shown

### Step 4: Configure Environment Variables

1. Open [.env.local](.env.local) in the Frontend directory
2. Replace the placeholder values with your actual Firebase config:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSy...your_actual_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abc123def456
```

### Step 5: Configure Authorized Domains (Important!)

1. In Firebase Console, go to **Authentication** → **Settings** tab
2. Scroll to **Authorized domains**
3. Make sure `localhost` is in the list (it should be by default)
4. When you deploy to production, add your production domain here

### Step 6: Backend Implementation

The backend needs to verify Firebase ID tokens. You'll need to:

1. **Install Firebase Admin SDK** in your backend:
   ```bash
   pip install firebase-admin
   ```

2. **Create an endpoint** at `/api/auth/google` that:
   - Receives the Firebase ID token
   - Verifies it using Firebase Admin SDK
   - Extracts user information (email, name, etc.)
   - Creates or logs in the user in your database
   - Returns your app's access token

**Example backend code (Python/FastAPI)**:

```python
from firebase_admin import auth, credentials, initialize_app
from fastapi import HTTPException

# Initialize Firebase Admin (do this once at startup)
cred = credentials.Certificate("path/to/serviceAccountKey.json")
initialize_app(cred)

@app.post("/api/auth/google")
async def google_login(request: GoogleLoginRequest):
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(request.id_token)
        
        # Extract user info
        email = decoded_token['email']
        name = decoded_token.get('name', '')
        firebase_uid = decoded_token['uid']
        
        # Check if user exists, create if not
        user = get_or_create_user(email=email, name=name, firebase_uid=firebase_uid)
        
        # Generate your app's access token
        access_token = create_access_token(user.id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "created_at": user.created_at.isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
```

### Step 7: Get Firebase Service Account Key (For Backend)

1. In Firebase Console, go to **Project Settings**
2. Go to **Service accounts** tab
3. Click **Generate new private key**
4. Download the JSON file
5. Save it securely in your backend directory
6. Add the path to your backend configuration

## 🧪 Testing

1. **Start the development server**:
   ```bash
   pnpm dev
   ```

2. **Test the Google sign-in**:
   - Navigate to http://localhost:3000/login
   - Click "Continue with Google"
   - A popup should appear for Google account selection
   - After selecting an account, you should be redirected to the dashboard

3. **Common issues**:
   - **Popup blocked**: Allow popups for localhost
   - **Unauthorized domain**: Make sure localhost is in Firebase authorized domains
   - **Backend error**: Ensure the backend endpoint is implemented and running

## 📁 Files Modified/Created

- ✅ [package.json](package.json) - Added Firebase dependency
- ✅ [lib/firebase.ts](lib/firebase.ts) - Firebase configuration and Google auth
- ✅ [context/auth-context.tsx](context/auth-context.tsx) - Implemented loginWithGoogle
- ✅ [lib/api-client.ts](lib/api-client.ts) - Added Google login API method
- ✅ [lib/api-config.ts](lib/api-config.ts) - Added Google login endpoint
- ✅ [.env.example](.env.example) - Added Firebase config template
- ✅ [.env.local](.env.local) - Ready for Firebase credentials

## 🔐 Security Notes

1. **Never commit** `.env.local` to version control
2. **Never expose** your Firebase service account key publicly
3. **Always verify** Firebase ID tokens on the backend
4. Firebase API keys are **safe to expose** in frontend (they're not secret)
5. The real security comes from **Firebase rules** and **backend validation**

## 📚 Additional Resources

- [Firebase Authentication Docs](https://firebase.google.com/docs/auth)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Google Sign-In Guide](https://firebase.google.com/docs/auth/web/google-signin)

## 🆘 Need Help?

If you encounter issues:
1. Check browser console for errors
2. Check backend logs
3. Verify Firebase configuration
4. Ensure all environment variables are set correctly
5. Make sure the backend endpoint is implemented and accessible
