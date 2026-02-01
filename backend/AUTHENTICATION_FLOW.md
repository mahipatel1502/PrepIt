# 🔐 PrepIt Authentication Flow

## System Architecture

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend  │  HTTP   │   FastAPI    │  Admin  │   Firebase   │
│  (Next.js)  │ ◄─────► │   Backend    │  SDK    │  Firestore   │
└─────────────┘         └──────────────┘ ◄─────► └──────────────┘
                              │
                              │ JWT
                              ▼
                        ┌──────────────┐
                        │  bcrypt      │
                        │  jose        │
                        └──────────────┘
```

## 📝 Signup Flow

```
User                    Frontend                Backend                 Firebase
  │                        │                       │                       │
  │ 1. Fill Form           │                       │                       │
  │ ──────────────────────►│                       │                       │
  │                        │                       │                       │
  │                        │ 2. POST /auth/signup  │                       │
  │                        │ ─────────────────────►│                       │
  │                        │    {full_name,        │                       │
  │                        │     email,            │                       │
  │                        │     password}         │                       │
  │                        │                       │                       │
  │                        │                       │ 3. Check if email     │
  │                        │                       │    exists             │
  │                        │                       │ ─────────────────────►│
  │                        │                       │                       │
  │                        │                       │ 4. Email not found    │
  │                        │                       │ ◄─────────────────────│
  │                        │                       │                       │
  │                        │                       │ 5. Hash password      │
  │                        │                       │    (bcrypt)           │
  │                        │                       │                       │
  │                        │                       │ 6. Create user doc    │
  │                        │                       │ ─────────────────────►│
  │                        │                       │                       │
  │                        │                       │ 7. User created       │
  │                        │                       │ ◄─────────────────────│
  │                        │                       │                       │
  │                        │                       │ 8. Generate JWT       │
  │                        │                       │    token              │
  │                        │                       │                       │
  │                        │ 9. Return token       │                       │
  │                        │    & user info        │                       │
  │                        │ ◄─────────────────────│                       │
  │                        │                       │                       │
  │ 10. Store token        │                       │                       │
  │ ◄──────────────────────│                       │                       │
  │     (localStorage)     │                       │                       │
```

## 🔐 Login Flow

```
User                    Frontend                Backend                 Firebase
  │                        │                       │                       │
  │ 1. Enter Credentials   │                       │                       │
  │ ──────────────────────►│                       │                       │
  │                        │                       │                       │
  │                        │ 2. POST /auth/login   │                       │
  │                        │ ─────────────────────►│                       │
  │                        │    {email,            │                       │
  │                        │     password}         │                       │
  │                        │                       │                       │
  │                        │                       │ 3. Find user by email │
  │                        │                       │ ─────────────────────►│
  │                        │                       │                       │
  │                        │                       │ 4. User found         │
  │                        │                       │ ◄─────────────────────│
  │                        │                       │                       │
  │                        │                       │ 5. Verify password    │
  │                        │                       │    (bcrypt.verify)    │
  │                        │                       │                       │
  │                        │                       │ 6. Password valid     │
  │                        │                       │                       │
  │                        │                       │ 7. Generate JWT       │
  │                        │                       │    token              │
  │                        │                       │                       │
  │                        │ 8. Return token       │                       │
  │                        │    & user info        │                       │
  │                        │ ◄─────────────────────│                       │
  │                        │                       │                       │
  │ 9. Store token         │                       │                       │
  │ ◄──────────────────────│                       │                       │
  │     (localStorage)     │                       │                       │
```

## 🔒 Protected Request Flow

```
User                    Frontend                Backend                 Firebase
  │                        │                       │                       │
  │ 1. Request Protected   │                       │                       │
  │    Resource            │                       │                       │
  │ ──────────────────────►│                       │                       │
  │                        │                       │                       │
  │                        │ 2. GET /auth/me       │                       │
  │                        │ ─────────────────────►│                       │
  │                        │    Authorization:     │                       │
  │                        │    Bearer <token>     │                       │
  │                        │                       │                       │
  │                        │                       │ 3. Verify JWT token   │
  │                        │                       │    (jose.jwt.decode)  │
  │                        │                       │                       │
  │                        │                       │ 4. Extract user_id    │
  │                        │                       │    from token         │
  │                        │                       │                       │
  │                        │                       │ 5. Fetch user data    │
  │                        │                       │ ─────────────────────►│
  │                        │                       │                       │
  │                        │                       │ 6. User data          │
  │                        │                       │ ◄─────────────────────│
  │                        │                       │                       │
  │                        │ 7. Return user data   │                       │
  │                        │ ◄─────────────────────│                       │
  │                        │                       │                       │
  │ 8. Display data        │                       │                       │
  │ ◄──────────────────────│                       │                       │
```

## ❌ Authentication Failure Flow

```
User                    Frontend                Backend
  │                        │                       │
  │ 1. Invalid Credentials │                       │
  │ ──────────────────────►│                       │
  │                        │                       │
  │                        │ 2. POST /auth/login   │
  │                        │ ─────────────────────►│
  │                        │                       │
  │                        │                       │ 3. Invalid password
  │                        │                       │    or email not found
  │                        │                       │
  │                        │ 4. 401 Unauthorized   │
  │                        │ ◄─────────────────────│
  │                        │    {"detail": "..."}  │
  │                        │                       │
  │ 5. Show error          │                       │
  │ ◄──────────────────────│                       │
```

## 🔑 JWT Token Structure

```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsImVtYWlsIjoiam9obkBleGFtcGxlLmNvbSIsImZ1bGxfbmFtZSI6IkpvaG4gRG9lIiwiZXhwIjoxNzA2ODY4MDAwfQ.signature

┌──────────────────────────────────────────────────────────────┐
│                        JWT Token                             │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  HEADER                                                      │
│  {                                                           │
│    "alg": "HS256",                                          │
│    "typ": "JWT"                                             │
│  }                                                           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  PAYLOAD                                                     │
│  {                                                           │
│    "sub": "user_123",           ← User ID                  │
│    "email": "john@example.com", ← User Email               │
│    "full_name": "John Doe",     ← User Name                │
│    "exp": 1706868000            ← Expiry (30 min)          │
│  }                                                           │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  SIGNATURE                                                   │
│  HMACSHA256(                                                │
│    base64UrlEncode(header) + "." +                          │
│    base64UrlEncode(payload),                                │
│    SECRET_KEY                                                │
│  )                                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 🗄️ Firestore Data Model

```
Firestore Database
│
└── users (Collection)
    │
    ├── user_abc123 (Document)
    │   ├── full_name: "John Doe"
    │   ├── email: "john@example.com"
    │   ├── password_hash: "$2b$12$..."
    │   ├── created_at: "2026-02-01T10:30:00"
    │   └── updated_at: "2026-02-01T10:30:00"
    │
    ├── user_def456 (Document)
    │   ├── full_name: "Jane Smith"
    │   ├── email: "jane@example.com"
    │   ├── password_hash: "$2b$12$..."
    │   ├── created_at: "2026-02-01T11:00:00"
    │   └── updated_at: "2026-02-01T11:00:00"
    │
    └── ...
```

## 🔐 Password Hashing

```
Plain Password           bcrypt                    Hashed Password
───────────────    ─────────────────    ─────────────────────────────────
                                        
"SecurePass123" ──► bcrypt.hash()   ──► "$2b$12$abcd...xyz123"
                    (with salt)         
                                        ├─ $2b        ← Algorithm
                                        ├─ $12        ← Cost factor
                                        ├─ $abcd...   ← Salt
                                        └─ xyz123     ← Hash


Verification:
"SecurePass123" ──► bcrypt.verify() ──► True/False
                    (against hash)
```

## 🔄 Middleware Flow

```
HTTP Request
     │
     ▼
┌────────────────────────────────────┐
│  1. CORS Middleware                │
│     - Check origin                 │
│     - Add CORS headers             │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│  2. Route Matching                 │
│     - Match path & method          │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│  3. Auth Middleware (if protected) │
│     - Extract Bearer token         │
│     - Verify JWT signature         │
│     - Check expiry                 │
│     - Inject user context          │
└────────────────────────────────────┘
     │
     ▼
┌────────────────────────────────────┐
│  4. Route Handler                  │
│     - Execute business logic       │
│     - Access Firebase              │
│     - Return response              │
└────────────────────────────────────┘
     │
     ▼
HTTP Response
```

## 📊 Security Layers

```
┌───────────────────────────────────────────┐
│         Security Layer 1: HTTPS           │  ← Transport Security
├───────────────────────────────────────────┤
│         Security Layer 2: CORS            │  ← Origin Validation
├───────────────────────────────────────────┤
│         Security Layer 3: JWT             │  ← Authentication
├───────────────────────────────────────────┤
│    Security Layer 4: Password Hashing     │  ← Data Protection
├───────────────────────────────────────────┤
│   Security Layer 5: Input Validation      │  ← Injection Prevention
├───────────────────────────────────────────┤
│   Security Layer 6: Firebase Rules        │  ← Database Security
└───────────────────────────────────────────┘
```

## 🎯 Token Lifecycle

```
Token Creation                  Token Usage                    Token Expiry
     │                              │                               │
     ▼                              ▼                               ▼
┌─────────┐                   ┌─────────┐                    ┌─────────┐
│ Signup  │                   │ Request │                    │  After  │
│   or    │──► JWT Token ────►│Protected│──► Verified ◄─────│30 min   │
│  Login  │                   │Endpoint │                    │(default)│
└─────────┘                   └─────────┘                    └─────────┘
                                                                   │
                                                                   ▼
                                                              Must login
                                                              again to get
                                                              new token
```

## 🚀 Complete Request/Response Cycle

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  Client                                                              │
│    │                                                                 │
│    │ 1. POST /api/auth/signup                                       │
│    │    {full_name, email, password}                                │
│    │                                                                 │
│    ▼                                                                 │
│  ┌────────────────────────────────────────┐                        │
│  │ FastAPI Backend                        │                        │
│  │                                        │                        │
│  │  ┌──────────────────────────────┐     │                        │
│  │  │ Pydantic Validation          │     │                        │
│  │  │ - Email format               │     │                        │
│  │  │ - Password strength          │     │                        │
│  │  │ - Required fields            │     │                        │
│  │  └──────────────────────────────┘     │                        │
│  │             │                          │                        │
│  │             ▼                          │                        │
│  │  ┌──────────────────────────────┐     │                        │
│  │  │ Business Logic               │     │                        │
│  │  │ - Check email exists         │◄───┼───► Firebase Firestore │
│  │  │ - Hash password              │     │                        │
│  │  │ - Create user document       │────┼───► Firebase Firestore │
│  │  │ - Generate JWT token         │     │                        │
│  │  └──────────────────────────────┘     │                        │
│  │             │                          │                        │
│  │             ▼                          │                        │
│  │  ┌──────────────────────────────┐     │                        │
│  │  │ Response                     │     │                        │
│  │  │ {token, user_info}           │     │                        │
│  │  └──────────────────────────────┘     │                        │
│  └────────────────────────────────────────┘                        │
│    │                                                                │
│    │ 2. Store token in localStorage                                │
│    │ 3. Include in future requests                                 │
│    │    Authorization: Bearer <token>                              │
│    │                                                                │
└──────────────────────────────────────────────────────────────────────┘
```

## 📱 Frontend Integration Points

```javascript
// 1. Signup
const signup = async (fullName, email, password) => {
  const res = await fetch('/api/auth/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, email, password })
  });
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
};

// 2. Login
const login = async (email, password) => {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
};

// 3. Protected Request
const fetchProtected = async (endpoint) => {
  const token = localStorage.getItem('token');
  const res = await fetch(endpoint, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
};

// 4. Logout
const logout = () => {
  localStorage.removeItem('token');
  // Optionally call backend logout endpoint
};
```

---

**Legend:**
- `│` : Sequential flow
- `►` : Action/Request
- `◄` : Response/Return
- `▼` : Next step
- `┌─┐` : Component/Layer boundary
