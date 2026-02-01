# PrepIt Backend API

FastAPI backend with **Firebase Authentication** and data preprocessing capabilities.

## ✨ Features

- 🔥 **Firebase Authentication** (email/password)
- 👤 User management (signup, login, profile)
- 📊 Dataset upload and processing
- 🔒 Protected routes with Firebase ID token verification
- 📝 Comprehensive API documentation
- ✅ Secure password validation (managed by Firebase)

## 🚀 Quick Start

### 1. Setup Firebase (5 minutes)
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Enable **Authentication** → **Email/Password** provider
4. Get your **Web API Key** from Project Settings → General

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file and add your Firebase credentials:
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-private-key-here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_WEB_API_KEY=your_firebase_web_api_key
```

**Get Firebase Credentials:**
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key" to download JSON
3. Copy the values from JSON to your .env file
4. Get Web API Key from Project Settings → General

**Or use the setup script:**
```bash
# Windows
setup_firebase_auth.bat

# Linux/Mac
bash setup_firebase_auth.sh
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

### 5. Test the API
Visit interactive docs: **http://localhost:8000/docs**

Or use curl:
```bash
# Signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"test123"}'
```

## 📚 Documentation

- 🎉 **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Overview and benefits
- 📖 **[FIREBASE_AUTH_MIGRATION.md](FIREBASE_AUTH_MIGRATION.md)** - Complete migration guide
- ⚡ **[FIREBASE_AUTH_QUICKREF.md](FIREBASE_AUTH_QUICKREF.md)** - API quick reference
- 🌐 **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user (returns Firebase tokens)
- `POST /api/auth/login` - Login user (returns Firebase tokens)
- `GET /api/auth/me` - Get current user info (requires Firebase ID token)
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Logout and revoke tokens

### Dataset (Protected)
- `POST /api/dataset/upload` - Upload and process dataset

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── models/
│   │   └── user.py         # User data models
│   ├── routes/
│   │   ├── auth.py         # Authentication endpoints (Firebase)
│   │   └── dataset.py      # Dataset endpoints
│   ├── services/
│   │   ├── analytics.py    # Data analytics
│   │   └── preprocessing.py # Data preprocessing
│   └── utils/
│       ├── auth_middleware.py  # Firebase token verification
│       ├── firebase_config.py  # Firebase initialization
│       └── file_handler.py     # File validation
├── data/
│   ├── raw/                # Raw uploaded files
│   └── processed/          # Processed datasets
├── .env                    # Environment variables (create this)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FIREBASE_TYPE` | Firebase service account type (service_account) | ✅ Yes |
| `FIREBASE_PROJECT_ID` | Your Firebase project ID | ✅ Yes |
| `FIREBASE_PRIVATE_KEY_ID` | Firebase private key ID | ✅ Yes |
| `FIREBASE_PRIVATE_KEY` | Firebase private key (with escaped newlines) | ✅ Yes |
| `FIREBASE_CLIENT_EMAIL` | Firebase service account email | ✅ Yes |
| `FIREBASE_CLIENT_ID` | Firebase client ID | ✅ Yes |
| `FIREBASE_CLIENT_CERT_URL` | Firebase client certificate URL | ❌ No |
| `FIREBASE_WEB_API_KEY` | Firebase Web API Key (from Firebase Console) | ✅ Yes |
| `ENVIRONMENT` | Environment (development/production) | ❌ No |

## 🔒 Security

- ✅ Enterprise-grade authentication via Firebase
- ✅ Secure password storage (managed by Firebase)
- ✅ Firebase ID tokens with 1-hour expiration
- ✅ Token refresh mechanism available
- ✅ Token revocation on logout
- ✅ Email validation on signup
- ✅ Minimum password requirements (6 characters)

## 🛠️ Technologies

- **FastAPI** - Modern Python web framework
- **Firebase Admin SDK** - Authentication & user management
- **Requests** - HTTP client for Firebase REST API
- **Pandas** - Data processing
- **Pydantic** - Data validation

## 💻 Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

## 🚢 Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Update CORS origins in `main.py`
3. Use production Firebase credentials
4. Ensure `FIREBASE_WEB_API_KEY` is configured
5. Enable rate limiting in Firebase Console

## 🆕 What's New

**Firebase Authentication Migration** (Latest)
- ✅ Migrated from custom JWT to Firebase Auth
- ✅ Removed Firestore user collection
- ✅ Simplified authentication flow
- ✅ 200+ lines of code removed
- 📚 See [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) for details

## ❓ Troubleshooting

**Error: "FIREBASE_WEB_API_KEY not configured"**
- Add the key to your `.env` file
- Get it from Firebase Console → Project Settings → Web API Key

**Error: "Authentication failed"**
- Check if Email/Password provider is enabled in Firebase Console
- Verify `FIREBASE_CREDENTIALS_PATH` is correct

**Need help?** Check [FIREBASE_AUTH_QUICKREF.md](FIREBASE_AUTH_QUICKREF.md) for common issues.
4. Use HTTPS in production
5. Set strong SECRET_KEY
6. Consider token blacklist for logout

## Support

For detailed setup instructions, see [AUTH_SETUP.md](AUTH_SETUP.md)
