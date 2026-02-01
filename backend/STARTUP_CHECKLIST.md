# 🚀 PrepIt Backend - Startup Checklist

## Pre-flight Checklist

### ☐ Step 1: Install Dependencies
```bash
cd d:\SGP\PrepIt-Data preproccesing\PrepIt\backend
pip install -r requirements.txt
```

**Expected packages:**
- fastapi
- uvicorn
- firebase-admin
- python-jose[cryptography]
- passlib[bcrypt]
- python-dotenv
- email-validator
- pandas, numpy, scikit-learn
- python-multipart, openpyxl

---

### ☐ Step 2: Generate Environment File

**Quick Method:**
```bash
python setup.py
```

**Manual Method:**
```bash
# Copy template
cp .env.example .env

# Edit .env and add Firebase credentials:
# Get these from Firebase Console > Project Settings > Service Accounts > Generate New Private Key
# Then copy the values from the downloaded JSON to .env:
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nyour-key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_WEB_API_KEY=your-web-api-key
```

**Note:** Firebase credentials are now stored directly in environment variables, no JSON file needed!

---

### ☐ Step 3: Setup Firebase

**Option A: Production**
1. ✅ Go to https://console.firebase.google.com/
2. ✅ Create/select project
3. ✅ Enable Firestore Database
4. ✅ Create Firestore in production mode
5. ✅ Go to Project Settings → Service Accounts
6. ✅ Click "Generate New Private Key"
7. ✅ Save JSON file to backend folder
8. ✅ Update .env: `FIREBASE_CREDENTIALS_PATH=firebase-service-account.json`

**Option B: Development (Emulator)**
```bash
npm install -g firebase-tools
firebase login
firebase init emulators
firebase emulators:start
```

---

### ☐ Step 4: Verify Configuration

**Check .env file exists:**
```bash
ls .env
```

**Should contain:**
```
SECRET_KEY=<your-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FIREBASE_CREDENTIALS_PATH=<path-to-firebase-json>
ENVIRONMENT=development
```

---

### ☐ Step 5: Start the Server

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### ☐ Step 6: Test the API

**Method 1: Automated Test**
```bash
python test_auth.py
```

**Method 2: Interactive Docs**
Open browser: http://localhost:8000/docs

**Method 3: Manual cURL**
```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

---

## 🎯 Success Indicators

✅ **Server Running**: `http://localhost:8000`
✅ **Docs Available**: `http://localhost:8000/docs`
✅ **Health Check**: Returns `{"status":"healthy"}`
✅ **No Import Errors**: All dependencies installed
✅ **Firebase Connected**: No connection errors in logs

---

## 🔍 Troubleshooting

### Issue: ModuleNotFoundError
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Firebase connection error
**Check:**
- ✅ FIREBASE_CREDENTIALS_PATH in .env is correct
- ✅ Firebase JSON file exists
- ✅ Firestore is enabled in Firebase Console

**Alternative (Development):**
Use Firebase emulator instead

### Issue: Port 8000 already in use
**Solution:**
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: SECRET_KEY not set
**Solution:**
```bash
python setup.py
# OR manually generate and add to .env
```

---

## 📋 Test Checklist

Run these tests to verify everything works:

### ☐ 1. Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

### ☐ 2. Signup New User
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"TestPass123"}'
```
Expected: Returns access_token and user info

### ☐ 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```
Expected: Returns access_token

### ☐ 4. Protected Endpoint
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <YOUR_TOKEN>"
```
Expected: Returns user info

### ☐ 5. Interactive Docs
Open: http://localhost:8000/docs
Expected: Swagger UI with all endpoints

---

## 🎉 Ready to Go!

When all checkboxes are ✅:
- Server is running on http://localhost:8000
- All tests pass
- Interactive docs working
- Firebase connected

**You're ready to integrate with the frontend!**

---

## 📚 Documentation Reference

- **Setup Guide**: [AUTH_SETUP.md](AUTH_SETUP.md)
- **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Main README**: [README.md](README.md)

---

## 🚀 Next Steps

1. ✅ Complete this checklist
2. 🔄 Test all endpoints
3. 🔄 Integrate with Frontend
4. 🔄 Deploy to production

---

**Need Help?** Check the documentation files or visit http://localhost:8000/docs for interactive API testing.
