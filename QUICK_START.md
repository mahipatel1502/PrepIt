# 🚀 PrepIt Quick Start Guide

Complete guide to run both backend and frontend together.

## 📋 Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- pnpm (or npm) installed
- Git installed

## 🎯 Complete Setup (First Time)

### 1️⃣ Backend Setup

```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Setup environment
python setup.py

# Configure Firebase (see AUTH_SETUP.md for details)
# - Get Firebase service account JSON
# - Update .env with path
# OR use Firebase emulator for development

# Start backend server
uvicorn app.main:app --reload
```

**Backend URL**: `http://localhost:8000`
**API Docs**: `http://localhost:8000/docs`

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend
cd Frontend

# Install dependencies
pnpm install
# or: npm install

# Environment is already configured (.env.local created)
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
pnpm dev
# or: npm run dev
```

**Frontend URL**: `http://localhost:3000`

## ⚡ Daily Workflow (After Initial Setup)

### Terminal 1: Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Terminal 2: Frontend
```bash
cd Frontend
pnpm dev
```

### Terminal 3: Firebase Emulator (Optional - for dev)
```bash
firebase emulators:start
```

## ✅ Verify Everything Works

### 1. Check Backend
```bash
# Open browser: http://localhost:8000/health
# Should see: {"status":"healthy"}
```

### 2. Check Frontend
```bash
# Open browser: http://localhost:3000
# Should see: PrepIt homepage
```

### 3. Test Authentication Flow

#### Signup
1. Go to `http://localhost:3000/signup`
2. Fill in:
   - Full Name: Test User
   - Email: test@example.com
   - Password: TestPass123
3. Click "Create account"
4. Should redirect to dashboard
5. Check browser localStorage has token

#### Login
1. Go to `http://localhost:3000/login`
2. Enter:
   - Email: test@example.com
   - Password: TestPass123
3. Click "Sign in"
4. Should redirect to dashboard

#### Auto-Login
1. After logging in, refresh page (F5)
2. Should remain logged in
3. Check Network tab for `/api/auth/me` call

#### Protected Route
1. Logout or clear localStorage
2. Try accessing `http://localhost:3000/dashboard`
3. Should redirect to login page

## 📁 Project Structure

```
PrepIt/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── models/            # Pydantic models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utilities (auth, firebase)
│   ├── .env                   # Environment vars (create this)
│   ├── requirements.txt       # Python dependencies
│   └── test_auth.py          # Test script
│
└── Frontend/                   # Next.js frontend
    ├── app/                    # App router pages
    │   ├── login/
    │   ├── signup/
    │   └── dashboard/
    ├── components/            # React components
    │   ├── layout/
    │   ├── dashboard/
    │   └── ui/
    ├── context/               # React contexts
    │   └── auth-context.tsx  # Auth state
    ├── hooks/                 # Custom hooks
    │   └── use-file-upload.ts
    ├── lib/                   # Utilities
    │   ├── api-client.ts     # API client
    │   └── api-config.ts     # API config
    ├── .env.local            # Local environment
    └── package.json          # Node dependencies
```

## 🔧 Environment Variables

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_CREDENTIALS_PATH=path/to/firebase.json
ENVIRONMENT=development
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_auth.py
```

### Manual Testing Checklist
- [ ] Backend health check works
- [ ] Frontend loads
- [ ] User can signup
- [ ] User can login
- [ ] User stays logged in on refresh
- [ ] Protected routes redirect when not logged in
- [ ] User can logout
- [ ] File upload works (when logged in)

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt

# Check if port 8000 is free
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules .next
pnpm install
pnpm dev
```

### Authentication not working
```bash
# 1. Check backend is running on port 8000
# 2. Check frontend .env.local has correct API URL
# 3. Check browser console for CORS errors
# 4. Check browser localStorage for token
# 5. Try logging in again
```

### CORS errors
```bash
# Backend should have CORS middleware configured
# In backend/app/main.py, check:
allow_origins=["http://localhost:3000", "*"]

# Restart backend after changes
```

### Firebase connection errors
```bash
# Option 1: Use Firebase emulator (recommended for dev)
firebase emulators:start

# Option 2: Use real Firebase
# - Ensure FIREBASE_CREDENTIALS_PATH in .env is correct
# - Check Firebase JSON file exists
# - Verify Firestore is enabled in Firebase Console
```

## 📊 Port Usage

| Service | Port | URL |
|---------|------|-----|
| Backend API | 8000 | http://localhost:8000 |
| Frontend | 3000 | http://localhost:3000 |
| Firebase Emulator UI | 4000 | http://localhost:4000 |
| Firestore Emulator | 8080 | http://localhost:8080 |

## 💡 Tips

### Development Best Practices
1. **Use two terminals** - one for backend, one for frontend
2. **Check both servers are running** before testing
3. **Clear browser cache** if seeing old data
4. **Check browser console** for errors
5. **Use API docs** at `http://localhost:8000/docs` for testing

### Hot Reload
- Backend: Auto-reloads on file changes (with `--reload` flag)
- Frontend: Auto-reloads on file changes (Next.js default)

### Stopping Servers
- Press `Ctrl + C` in terminal to stop servers
- Or close the terminal window

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Backend README](backend/README.md) | Backend overview |
| [Backend AUTH_SETUP](backend/AUTH_SETUP.md) | Detailed auth setup |
| [Backend API_REFERENCE](backend/API_REFERENCE.md) | API endpoints |
| [Frontend INTEGRATION](Frontend/FRONTEND_INTEGRATION.md) | Frontend integration guide |

## 🎉 You're All Set!

When both servers are running:
1. ✅ Backend API: `http://localhost:8000`
2. ✅ Frontend App: `http://localhost:3000`
3. ✅ API Documentation: `http://localhost:8000/docs`

**Start building your data preprocessing platform!**

---

## Quick Commands Reference

```bash
# Backend
cd backend
pip install -r requirements.txt     # Install deps
python setup.py                     # Setup env
uvicorn app.main:app --reload       # Run server
python test_auth.py                 # Test auth

# Frontend
cd Frontend
pnpm install                        # Install deps
pnpm dev                           # Run dev server
pnpm build                         # Build for production
pnpm start                         # Run production build

# Both (in separate terminals)
cd backend && uvicorn app.main:app --reload
cd Frontend && pnpm dev
```
