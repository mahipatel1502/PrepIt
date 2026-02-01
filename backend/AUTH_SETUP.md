# PrepIt Backend - Authentication Setup

## Overview
JWT-based authentication system integrated with Google Firebase Firestore for user management.

## Features
✅ User Registration (Signup) with full name, email, and password
✅ User Login with JWT token generation
✅ Password hashing with bcrypt
✅ JWT token-based authentication
✅ Protected routes with middleware
✅ User profile management
✅ Password change functionality
✅ Firebase Firestore integration

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Firebase Setup

#### Option A: Using Firebase Service Account (Production)
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project or create a new one
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the JSON file in your backend directory
6. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
7. Update `.env` with your configuration:
   ```
   SECRET_KEY=your-super-secret-jwt-key-here
   FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-service-account.json
   ```

#### Option B: Using Firebase Emulator (Development)
```bash
npm install -g firebase-tools
firebase init emulators
firebase emulators:start
```

### 3. Generate a Secure SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and paste it in your `.env` file.

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### Authentication Endpoints

#### 1. **POST** `/api/auth/signup`
Register a new user account.

**Request Body:**
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 digit

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "abc123...",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-02-01T10:30:00"
  }
}
```

#### 2. **POST** `/api/auth/login`
Login with email and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "abc123...",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-02-01T10:30:00"
  }
}
```

#### 3. **GET** `/api/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user_id": "abc123...",
  "full_name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-02-01T10:30:00"
}
```

#### 4. **PUT** `/api/auth/me`
Update user information (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

#### 5. **POST** `/api/auth/change-password`
Change user password (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}
```

#### 6. **POST** `/api/auth/logout`
Logout (client should discard token).

**Headers:**
```
Authorization: Bearer <access_token>
```

### Protected Dataset Endpoint

#### **POST** `/api/dataset/upload`
Upload and process dataset (requires authentication).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data:**
```
file: [your_file.csv or your_file.xlsx]
```

## Testing the API

### Using cURL

**Signup:**
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Get User Info:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Upload Dataset:**
```bash
curl -X POST http://localhost:8000/api/dataset/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@path/to/your/file.csv"
```

### Using the Interactive Docs
Visit `http://localhost:8000/docs` for Swagger UI documentation where you can test all endpoints interactively.

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   └── user.py            # User Pydantic models
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   └── dataset.py         # Dataset endpoints
│   ├── services/
│   │   ├── analytics.py       # Data analytics
│   │   └── preprocessing.py   # Data preprocessing
│   └── utils/
│       ├── auth_middleware.py  # JWT authentication middleware
│       ├── firebase_config.py  # Firebase initialization
│       ├── jwt_handler.py      # JWT utilities
│       └── file_handler.py     # File validation
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Environment template
└── requirements.txt           # Python dependencies
```

## Security Best Practices

1. **Never commit `.env` file** - Add it to `.gitignore`
2. **Use strong SECRET_KEY** - Generate with `secrets.token_urlsafe(32)`
3. **HTTPS in production** - Always use HTTPS for API in production
4. **Configure CORS properly** - Update `allow_origins` in `main.py` for production
5. **Secure Firebase credentials** - Keep service account JSON files secure
6. **Token expiration** - Tokens expire after 30 minutes by default
7. **Password requirements** - Enforced: min 8 chars, 1 uppercase, 1 digit

## Firebase Firestore Structure

### Users Collection: `users`
```
users/
  {user_id}/
    - full_name: string
    - email: string
    - password_hash: string
    - created_at: timestamp
    - updated_at: timestamp
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key | (required) |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | 30 |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase JSON | (optional for dev) |
| `ENVIRONMENT` | Environment mode | development |

## Troubleshooting

### Firebase Connection Issues
- Ensure Firebase credentials file path is correct
- Check if Firestore is enabled in Firebase Console
- For development, use Firebase emulator

### JWT Token Errors
- Verify SECRET_KEY is set in `.env`
- Check token hasn't expired (30 min default)
- Ensure token is sent with "Bearer " prefix

### Password Validation Errors
- Password must be at least 8 characters
- Must contain at least 1 uppercase letter
- Must contain at least 1 digit

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up Firebase project
3. ✅ Configure `.env` file
4. ✅ Run the server
5. 🔄 Test endpoints using `/docs`
6. 🔄 Integrate with frontend
7. 🔄 Deploy to production

## Support
For issues or questions, refer to the [FastAPI documentation](https://fastapi.tiangolo.com/) and [Firebase documentation](https://firebase.google.com/docs).
