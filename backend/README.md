# PrepIt Backend API

FastAPI backend with JWT authentication and Firebase Firestore integration for data preprocessing and analytics.

## Features

- 🔐 JWT-based authentication
- 👤 User management (signup, login, profile)
- 🔥 Firebase Firestore integration
- 📊 Dataset upload and processing
- 🔒 Protected routes with middleware
- 📝 Comprehensive API documentation
- ✅ Password validation and hashing

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example env file
cp .env.example .env

# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with your SECRET_KEY and Firebase credentials
```

### 3. Setup Firebase
See [AUTH_SETUP.md](AUTH_SETUP.md) for detailed Firebase configuration.

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

Server will start at `http://localhost:8000`

### 5. Test the API
```bash
# Run automated tests
python test_auth.py

# Or visit interactive docs
# http://localhost:8000/docs
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/me` - Update user info
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/logout` - Logout

### Dataset (Protected)
- `POST /api/dataset/upload` - Upload and process dataset

## Documentation

- 📖 [Authentication Setup Guide](AUTH_SETUP.md) - Complete setup instructions
- 🌐 [API Documentation](http://localhost:8000/docs) - Interactive Swagger UI (when server is running)
- 📚 [ReDoc](http://localhost:8000/redoc) - Alternative API documentation

## Project Structure

```
backend/
├── app/
│   ├── main.py              # Application entry point
│   ├── models/
│   │   └── user.py         # User data models
│   ├── routes/
│   │   ├── auth.py         # Authentication endpoints
│   │   └── dataset.py      # Dataset endpoints
│   ├── services/
│   │   ├── analytics.py    # Data analytics
│   │   └── preprocessing.py # Data preprocessing
│   └── utils/
│       ├── auth_middleware.py  # Auth middleware
│       ├── firebase_config.py  # Firebase setup
│       ├── jwt_handler.py      # JWT utilities
│       └── file_handler.py     # File validation
├── data/
│   ├── raw/                # Raw uploaded files
│   └── processed/          # Processed datasets
├── .env                    # Environment variables (create this)
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
├── test_auth.py          # Authentication tests
└── README.md             # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | JWT secret key | ✅ Yes |
| `ALGORITHM` | JWT algorithm (default: HS256) | ❌ No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry (default: 30) | ❌ No |
| `FIREBASE_CREDENTIALS_PATH` | Path to Firebase JSON | ⚠️ Production |

## Security

- Passwords are hashed with bcrypt
- JWT tokens expire after 30 minutes
- Protected routes require valid Bearer token
- Email validation on signup
- Strong password requirements enforced

## Technologies

- **FastAPI** - Modern Python web framework
- **Firebase Admin SDK** - Firestore database
- **python-jose** - JWT token handling
- **passlib** - Password hashing
- **Pandas** - Data processing
- **Pydantic** - Data validation

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
python test_auth.py
```

## Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Update CORS origins in `main.py`
3. Use production Firebase credentials
4. Use HTTPS in production
5. Set strong SECRET_KEY
6. Consider token blacklist for logout

## Support

For detailed setup instructions, see [AUTH_SETUP.md](AUTH_SETUP.md)
