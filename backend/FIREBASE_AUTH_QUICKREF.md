# Firebase Authentication Quick Reference

## 🔑 Environment Setup

Add to `.env`:
```env
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_WEB_API_KEY=your_web_api_key_from_firebase_console
```

## 📝 API Endpoints

### Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "id_token": "eyJhbGc...",
  "refresh_token": "AOEOulZ...",
  "expires_in": 3600,
  "user": {
    "user_id": "firebase_uid",
    "full_name": "John Doe",
    "email": "john@example.com",
    "email_verified": false
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response:** Same as signup

### Get Current User
```http
GET /auth/me
Authorization: Bearer {id_token}
```

**Response:**
```json
{
  "user_id": "firebase_uid",
  "full_name": "John Doe",
  "email": "john@example.com",
  "email_verified": false
}
```

### Update Profile
```http
PUT /auth/me
Authorization: Bearer {id_token}
Content-Type: application/json

{
  "full_name": "Jane Doe"
}
```

### Change Password
```http
POST /auth/change-password
Authorization: Bearer {id_token}
Content-Type: application/json

{
  "new_password": "newsecurepass456"
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {id_token}
```

## 🔄 Token Refresh (Client-Side)

Use Firebase REST API directly:
```javascript
const response = await fetch(
  `https://securetoken.googleapis.com/v1/token?key=${FIREBASE_WEB_API_KEY}`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'refresh_token',
      refresh_token: your_refresh_token
    })
  }
);

const { id_token, refresh_token, expires_in } = await response.json();
```

## ⚠️ Important Notes

1. **ID tokens expire in 1 hour** - implement refresh logic
2. **Store 3 values**: `id_token`, `refresh_token`, `token_expires_at`
3. **Always use id_token** in Authorization header
4. **Password minimum**: 6 characters (Firebase requirement)
5. **No old password needed** for password change (Firebase handles security)

## 🚨 Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| `EMAIL_EXISTS` | Email already registered | Use login instead |
| `INVALID_PASSWORD` | Wrong password | Check credentials |
| `EMAIL_NOT_FOUND` | User doesn't exist | Sign up first |
| `Token has expired` | ID token expired | Refresh token |
| `Token has been revoked` | User logged out elsewhere | Login again |

## 🎯 Frontend Integration Example

```javascript
// Store tokens after login/signup
function storeTokens(response) {
  localStorage.setItem('id_token', response.id_token);
  localStorage.setItem('refresh_token', response.refresh_token);
  localStorage.setItem('token_expires_at', Date.now() + (response.expires_in * 1000));
}

// Check if token is expired
function isTokenExpired() {
  const expiresAt = localStorage.getItem('token_expires_at');
  return !expiresAt || Date.now() >= parseInt(expiresAt);
}

// Refresh token if needed
async function getValidToken() {
  if (isTokenExpired()) {
    const newToken = await refreshToken();
    return newToken;
  }
  return localStorage.getItem('id_token');
}

// Make authenticated request
async function apiCall(url, options = {}) {
  const token = await getValidToken();
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
}
```

## ✅ Testing Commands

```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Get current user
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ID_TOKEN"
```
