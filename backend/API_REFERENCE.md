# 🎯 PrepIt API Quick Reference

## Base URL
```
http://localhost:8000
```

## Authentication Endpoints

### 📝 Signup
**POST** `/api/auth/signup`

Request:
```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Response (201):
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "user_id": "abc123",
    "full_name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-02-01T10:30:00"
  }
}
```

---

### 🔐 Login
**POST** `/api/auth/login`

Request:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

Response (200):
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": { ... }
}
```

---

### 👤 Get User Info
**GET** `/api/auth/me`

Headers:
```
Authorization: Bearer <token>
```

Response (200):
```json
{
  "user_id": "abc123",
  "full_name": "John Doe",
  "email": "john@example.com",
  "created_at": "2026-02-01T10:30:00"
}
```

---

### ✏️ Update User Info
**PUT** `/api/auth/me`

Headers:
```
Authorization: Bearer <token>
```

Request:
```json
{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

Response (200):
```json
{
  "user_id": "abc123",
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "created_at": "2026-02-01T10:30:00"
}
```

---

### 🔑 Change Password
**POST** `/api/auth/change-password`

Headers:
```
Authorization: Bearer <token>
```

Request:
```json
{
  "old_password": "SecurePass123",
  "new_password": "NewSecurePass456"
}
```

Response (200):
```json
{
  "message": "Password changed successfully"
}
```

---

### 🚪 Logout
**POST** `/api/auth/logout`

Headers:
```
Authorization: Bearer <token>
```

Response (200):
```json
{
  "message": "Logged out successfully"
}
```

---

## Dataset Endpoints (Protected)

### 📤 Upload Dataset
**POST** `/api/dataset/upload`

Headers:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

Form Data:
```
file: [your_file.csv or your_file.xlsx]
```

Response (200):
```json
{
  "message": "Dataset processed successfully",
  "user_id": "abc123",
  "preprocessing_report": { ... },
  "analytics": { ... }
}
```

---

## Health & Info

### ✅ Health Check
**GET** `/health`

Response (200):
```json
{
  "status": "healthy"
}
```

---

### ℹ️ API Info
**GET** `/`

Response (200):
```json
{
  "message": "PrepIt API is running",
  "version": "1.0.0"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters long",
      "type": "value_error"
    }
  ]
}
```

---

## Password Requirements

✅ Minimum 8 characters
✅ At least 1 uppercase letter
✅ At least 1 digit

---

## Token Information

- **Type**: JWT (JSON Web Token)
- **Algorithm**: HS256
- **Expiry**: 30 minutes (default)
- **Format**: `Authorization: Bearer <token>`

---

## Quick Test Commands

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"TestPass123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

### Get User
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Upload File
```bash
curl -X POST http://localhost:8000/api/dataset/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"
```

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |
