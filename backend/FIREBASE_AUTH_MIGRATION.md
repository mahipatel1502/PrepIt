# Firebase Authentication Migration Guide

## Overview
The authentication system has been migrated from manual user storage in Firestore to **Firebase Authentication** with email/password provider.

## What Changed

### 🔄 Authentication Flow
- **Before**: Custom JWT tokens + password hashing + Firestore user storage
- **After**: Firebase Authentication with ID tokens + email/password provider

### 🗑️ Removed Components
- ❌ Custom JWT token generation (`jwt_handler.py`)
- ❌ Password hashing utilities (bcrypt/passlib)
- ❌ Firestore user collection storage
- ❌ Manual password validation logic
- ❌ Custom token expiration handling

### ✅ New Components
- ✅ Firebase Authentication SDK
- ✅ Firebase ID token verification
- ✅ Firebase REST API for sign-in
- ✅ Built-in password strength validation
- ✅ Token revocation support

## Setup Instructions

### 1. Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Navigate to **Authentication** → **Sign-in method**
4. Enable **Email/Password** provider
5. (Optional) Enable **Email link (passwordless sign-in)** if needed

### 2. Get Firebase Web API Key

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Under **General** tab, find **Web API Key**
3. Copy the API key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### 3. Update Environment Variables

Update your `.env` file with individual Firebase credentials (no JSON file needed):

```env
# Firebase Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
FIREBASE_WEB_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**How to get these values:**
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key" to download JSON
3. Copy the values from the downloaded JSON to your .env file
4. For Web API Key: Project Settings → General

**Note**: Remove the old JWT configuration (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Updated dependencies:
- ✅ `firebase-admin` (already included)
- ✅ `requests` (for Firebase REST API)
- ❌ `python-jose` (removed)
- ❌ `passlib` (removed)
- ❌ `bcrypt` (removed)

## API Changes

### Token Response Structure

**Before:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "user_id": "doc123",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**After:**
```json
{
  "id_token": "eyJhbGc...",
  "refresh_token": "AOEOulZ...",
  "expires_in": 3600,
  "user": {
    "user_id": "firebase_uid_123",
    "full_name": "John Doe",
    "email": "john@example.com",
    "email_verified": false
  }
}
```

### User Response Structure

**Changed Fields:**
- ❌ `created_at` (timestamp) → No longer available
- ✅ `email_verified` (boolean) → New field

### Updated Endpoints

All endpoints remain the same, but now use Firebase Auth:

#### POST `/auth/signup`
- Creates user in Firebase Authentication
- Returns Firebase ID token and refresh token
- Password requirements: minimum 6 characters (Firebase default)

#### POST `/auth/login`
- Authenticates using Firebase REST API
- Returns Firebase ID token and refresh token
- Tokens expire after 1 hour (default)

#### GET `/auth/me`
- Verifies Firebase ID token
- Returns user info from Firebase Auth

#### PUT `/auth/me`
- Updates display name in Firebase Auth
- Email updates now require re-authentication (Firebase security)

#### POST `/auth/change-password`
- Updates password in Firebase Auth
- No longer requires old password (can be added with re-authentication)

#### POST `/auth/logout`
- Revokes all refresh tokens for the user
- Client must discard tokens

## Frontend Changes Required

### 1. Update Token Storage

Store **three** values instead of one:
```javascript
// Before
localStorage.setItem('access_token', response.access_token);

// After
localStorage.setItem('id_token', response.id_token);
localStorage.setItem('refresh_token', response.refresh_token);
localStorage.setItem('token_expires_at', Date.now() + (response.expires_in * 1000));
```

### 2. Update Authorization Headers

```javascript
// Before and After - same!
headers: {
  'Authorization': `Bearer ${id_token}`
}
```

### 3. Implement Token Refresh

Firebase ID tokens expire after 1 hour. Implement refresh logic:

```javascript
async function refreshToken() {
  const refresh_token = localStorage.getItem('refresh_token');
  const response = await fetch(
    `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_WEB_API_KEY}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'refresh_token',
        refresh_token: refresh_token
      })
    }
  );
  
  const data = await response.json();
  localStorage.setItem('id_token', data.id_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('token_expires_at', Date.now() + (data.expires_in * 1000));
  
  return data.id_token;
}
```

### 4. Check Token Expiration

```javascript
function isTokenExpired() {
  const expiresAt = localStorage.getItem('token_expires_at');
  return Date.now() >= parseInt(expiresAt);
}

// Before each API call
if (isTokenExpired()) {
  await refreshToken();
}
```

## Benefits of Migration

### 🔒 Security
- ✅ Industry-standard authentication
- ✅ Built-in token revocation
- ✅ Secure password storage (handled by Firebase)
- ✅ Automatic security updates

### 🚀 Features
- ✅ Email verification out of the box
- ✅ Password reset emails
- ✅ Multi-factor authentication (easy to add)
- ✅ Social auth providers (easy to add)

### 🛠️ Maintenance
- ✅ Less code to maintain
- ✅ No password hashing logic
- ✅ No custom token generation
- ✅ Firebase handles scalability

### 📊 Monitoring
- ✅ Firebase Console shows all users
- ✅ Built-in analytics
- ✅ Authentication logs

## Testing

### Test Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ID_TOKEN_HERE"
```

## Troubleshooting

### Error: "FIREBASE_WEB_API_KEY not configured"
- Add `FIREBASE_WEB_API_KEY` to your `.env` file
- Get it from Firebase Console → Project Settings

### Error: "EMAIL_EXISTS" during signup
- The email is already registered
- User should try logging in instead

### Error: "INVALID_PASSWORD" or "EMAIL_NOT_FOUND"
- Credentials are incorrect
- Check email and password

### Error: "Token has expired"
- Frontend needs to refresh the token
- Implement token refresh logic

### Error: "Token has been revoked"
- User logged out from another device
- User needs to log in again

## Migration Checklist

- [x] Enable Firebase Authentication Email/Password provider
- [x] Get Firebase Web API Key
- [x] Update `.env` file with `FIREBASE_WEB_API_KEY`
- [x] Install updated dependencies
- [ ] Update frontend token storage logic
- [ ] Implement token refresh in frontend
- [ ] Test signup, login, and protected routes
- [ ] Update frontend user profile to show `email_verified`
- [ ] (Optional) Implement email verification flow
- [ ] (Optional) Implement password reset flow

## Next Steps

1. **Email Verification**: Add email verification on signup
2. **Password Reset**: Implement forgot password flow
3. **Social Auth**: Add Google/GitHub login
4. **MFA**: Enable multi-factor authentication
5. **Rate Limiting**: Configure Firebase security rules

## Support

For issues or questions:
1. Check Firebase Console for authentication logs
2. Verify environment variables are set correctly
3. Test with Firebase Auth REST API directly
4. Review Firebase Auth documentation: https://firebase.google.com/docs/auth
