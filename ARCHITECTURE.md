# 🏗️ PrepIt Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Browser                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Next.js Frontend (Port 3000)                     │  │
│  │                                                               │  │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐│  │
│  │  │  Pages          │  │  Components  │  │  Contexts       ││  │
│  │  │  - /login       │  │  - UI        │  │  - AuthContext  ││  │
│  │  │  - /signup      │  │  - Layout    │  │  - ThemeContext ││  │
│  │  │  - /dashboard   │  │  - Protected │  │                 ││  │
│  │  │  - /upload      │  │  - Dashboard │  │                 ││  │
│  │  └─────────────────┘  └──────────────┘  └─────────────────┘│  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐│  │
│  │  │         API Client Layer (lib/api-client.ts)            ││  │
│  │  │  - JWT token management                                 ││  │
│  │  │  - HTTP request/response handling                       ││  │
│  │  │  - Error transformation                                 ││  │
│  │  └─────────────────────────────────────────────────────────┘│  │
│  │                                                               │  │
│  │  ┌─────────────────────────────────────────────────────────┐│  │
│  │  │         localStorage (prepit_auth_token)                ││  │
│  │  └─────────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ HTTP/HTTPS
                                   │ Authorization: Bearer <JWT>
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    CORS Middleware                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                   │
│                                   ▼
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Route Handlers                             │  │
│  │                                                               │  │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐│  │
│  │  │  Auth Routes    │  │Dataset Routes│  │  Health Check   ││  │
│  │  │  - /auth/signup │  │  - /upload   │  │  - /health      ││  │
│  │  │  - /auth/login  │  │  (protected) │  │  - /            ││  │
│  │  │  - /auth/me     │  │              │  │                 ││  │
│  │  │  - /auth/logout │  │              │  │                 ││  │
│  │  └─────────────────┘  └──────────────┘  └─────────────────┘│  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                   │
│                                   ▼
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Auth Middleware (Depends)                        │  │
│  │  - Extract Bearer token                                       │  │
│  │  - Verify JWT signature                                       │  │
│  │  - Check token expiration                                     │  │
│  │  - Inject user context                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                   │
│                                   ▼
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Business Logic                              │  │
│  │                                                               │  │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐│  │
│  │  │  JWT Handler    │  │ Preprocessing│  │  Analytics      ││  │
│  │  │  - Create token │  │  Service     │  │  Service        ││  │
│  │  │  - Verify token │  │  - Clean data│  │  - Statistics   ││  │
│  │  │  - Hash password│  │  - Transform │  │  - Reports      ││  │
│  │  └─────────────────┘  └──────────────┘  └─────────────────┘│  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                   │
│                                   ▼
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            Firebase Admin SDK                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Firebase Admin API
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Google Firebase Cloud                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Firestore Database                           │  │
│  │                                                               │  │
│  │  Collection: users                                            │  │
│  │  ├── {user_id_1}                                             │  │
│  │  │   ├── full_name: "John Doe"                              │  │
│  │  │   ├── email: "john@example.com"                          │  │
│  │  │   ├── password_hash: "$2b$12$..."                        │  │
│  │  │   ├── created_at: "2026-02-01T10:30:00"                  │  │
│  │  │   └── updated_at: "2026-02-01T10:30:00"                  │  │
│  │  │                                                            │  │
│  │  ├── {user_id_2}                                             │  │
│  │  │   └── ...                                                 │  │
│  │  │                                                            │  │
│  │  └── {user_id_n}                                             │  │
│  │      └── ...                                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

### User Signup Flow
```
User Browser                    Frontend                Backend                Firebase
     │                             │                       │                       │
     │ 1. Fill signup form         │                       │                       │
     │──────────────────────────►  │                       │                       │
     │                             │                       │                       │
     │                             │ 2. Call apiClient     │                       │
     │                             │    .signup()          │                       │
     │                             │                       │                       │
     │                             │ 3. POST /auth/signup  │                       │
     │                             │ ───────────────────►  │                       │
     │                             │    {full_name,        │                       │
     │                             │     email,            │                       │
     │                             │     password}         │                       │
     │                             │                       │                       │
     │                             │                       │ 4. Validate data      │
     │                             │                       │    (Pydantic)         │
     │                             │                       │                       │
     │                             │                       │ 5. Check email exists │
     │                             │                       │ ───────────────────► │
     │                             │                       │                       │
     │                             │                       │ 6. Email available    │
     │                             │                       │ ◄───────────────────  │
     │                             │                       │                       │
     │                             │                       │ 7. Hash password      │
     │                             │                       │    (bcrypt)           │
     │                             │                       │                       │
     │                             │                       │ 8. Create user doc    │
     │                             │                       │ ───────────────────► │
     │                             │                       │                       │
     │                             │                       │ 9. Document created   │
     │                             │                       │ ◄───────────────────  │
     │                             │                       │                       │
     │                             │                       │ 10. Generate JWT      │
     │                             │                       │     {sub: user_id,    │
     │                             │                       │      email, name}     │
     │                             │                       │                       │
     │                             │ 11. Response          │                       │
     │                             │ ◄───────────────────  │                       │
     │                             │    {access_token,     │                       │
     │                             │     user}             │                       │
     │                             │                       │                       │
     │                             │ 12. Store token       │                       │
     │                             │     in localStorage   │                       │
     │                             │                       │                       │
     │                             │ 13. Update AuthContext│                       │
     │                             │     setUser(user)     │                       │
     │                             │                       │                       │
     │ 14. Redirect to /dashboard  │                       │                       │
     │ ◄────────────────────────── │                       │                       │
```

### Protected Route Access Flow
```
User Browser                    Frontend                Backend                Firebase
     │                             │                       │                       │
     │ 1. Navigate to /dashboard   │                       │                       │
     │──────────────────────────►  │                       │                       │
     │                             │                       │                       │
     │                             │ 2. ProtectedRoute     │                       │
     │                             │    checks auth        │                       │
     │                             │                       │                       │
     │                             │ 3. Get token from     │                       │
     │                             │    localStorage       │                       │
     │                             │                       │                       │
     │                             │ 4. GET /auth/me       │                       │
     │                             │ ───────────────────►  │                       │
     │                             │    Authorization:     │                       │
     │                             │    Bearer <token>     │                       │
     │                             │                       │                       │
     │                             │                       │ 5. Extract token      │
     │                             │                       │    from header        │
     │                             │                       │                       │
     │                             │                       │ 6. Verify JWT         │
     │                             │                       │    signature          │
     │                             │                       │                       │
     │                             │                       │ 7. Extract user_id    │
     │                             │                       │    from token         │
     │                             │                       │                       │
     │                             │                       │ 8. Fetch user data    │
     │                             │                       │ ───────────────────► │
     │                             │                       │                       │
     │                             │                       │ 9. User data          │
     │                             │                       │ ◄───────────────────  │
     │                             │                       │                       │
     │                             │ 10. Response          │                       │
     │                             │ ◄───────────────────  │                       │
     │                             │    {user_id,          │                       │
     │                             │     full_name,        │                       │
     │                             │     email}            │                       │
     │                             │                       │                       │
     │                             │ 11. Update context    │                       │
     │                             │     setUser(user)     │                       │
     │                             │                       │                       │
     │ 12. Render dashboard        │                       │                       │
     │ ◄────────────────────────── │                       │                       │
```

## Technology Stack

```
┌────────────────────────────────────────────────────────────┐
│                      Frontend Stack                         │
├────────────────────────────────────────────────────────────┤
│  Framework:        Next.js 16 (App Router)                 │
│  Language:         TypeScript                               │
│  UI Library:       React 19                                 │
│  Styling:          Tailwind CSS                             │
│  Components:       Radix UI + shadcn/ui                     │
│  State:            React Context API                        │
│  HTTP Client:      Fetch API                                │
│  Storage:          localStorage (JWT tokens)                │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                      Backend Stack                          │
├────────────────────────────────────────────────────────────┤
│  Framework:        FastAPI                                  │
│  Language:         Python 3.8+                              │
│  Database:         Firebase Firestore                       │
│  Authentication:   JWT (python-jose)                        │
│  Password:         bcrypt (passlib)                         │
│  Validation:       Pydantic                                 │
│  CORS:            FastAPI CORS Middleware                   │
│  Data Processing:  Pandas, NumPy, scikit-learn             │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                    Database & Cloud                         │
├────────────────────────────────────────────────────────────┤
│  Database:         Google Firebase Firestore (NoSQL)       │
│  Admin SDK:        Firebase Admin Python SDK               │
│  Storage:          Firestore Collections                    │
│  Hosting:          Local Dev / Cloud Deployment Ready      │
└────────────────────────────────────────────────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────┐
│                  Security Architecture                   │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Transport  │  │     Auth     │  │    Data      │
│   Security   │  │   Security   │  │  Security    │
├──────────────┤  ├──────────────┤  ├──────────────┤
│  - HTTPS     │  │  - JWT       │  │  - Bcrypt    │
│  - TLS/SSL   │  │  - Bearer    │  │  - Hashing   │
│  (Production)│  │    Token     │  │  - Validation│
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │   CORS       │
                  │   Middleware │
                  └──────────────┘
                           │
                           ▼
                  ┌──────────────┐
                  │   Firebase   │
                  │   Security   │
                  │   Rules      │
                  └──────────────┘
```

## Data Flow

### Authentication Token Flow
```
┌─────────┐        ┌─────────┐        ┌──────────┐
│  Login  │───────►│  JWT    │───────►│localStorage│
│  /Signup│        │ Created │        │   Token   │
└─────────┘        └─────────┘        └──────────┘
                                             │
                                             │
                      ┌──────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  Every Request│
              │  to Backend   │
              │  Authorization│
              │  Header       │
              └───────────────┘
                      │
                      ▼
              ┌───────────────┐
              │  Backend      │
              │  Verifies JWT │
              │  Signature    │
              └───────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
  ┌──────────┐              ┌──────────┐
  │  Valid   │              │ Invalid  │
  │  Allow   │              │ Reject   │
  │  Access  │              │ 401      │
  └──────────┘              └──────────┘
```

### File Upload Flow
```
User                    Frontend              Backend              Firestore
 │                         │                     │                     │
 │ 1. Select File          │                     │                     │
 │────────────────────────►│                     │                     │
 │                         │                     │                     │
 │                         │ 2. Validate         │                     │
 │                         │    - Type (.csv)    │                     │
 │                         │    - Size (< 50MB)  │                     │
 │                         │                     │                     │
 │                         │ 3. POST /upload     │                     │
 │                         │ ───────────────────►│                     │
 │                         │    FormData(file)   │                     │
 │                         │    Bearer <token>   │                     │
 │                         │                     │                     │
 │                         │                     │ 4. Verify JWT       │
 │                         │                     │                     │
 │                         │                     │ 5. Read & Parse     │
 │                         │                     │    (Pandas)         │
 │                         │                     │                     │
 │                         │                     │ 6. Preprocess       │
 │                         │                     │    - Clean          │
 │                         │                     │    - Transform      │
 │                         │                     │                     │
 │                         │                     │ 7. Analyze          │
 │                         │                     │    - Stats          │
 │                         │                     │    - Report         │
 │                         │                     │                     │
 │                         │                     │ 8. Store metadata   │
 │                         │                     │ ───────────────────►│
 │                         │                     │                     │
 │                         │ 9. Response         │                     │
 │                         │ ◄───────────────────│                     │
 │                         │    {report,         │                     │
 │                         │     analytics}      │                     │
 │                         │                     │                     │
 │ 10. Display Results     │                     │                     │
 │◄────────────────────────│                     │                     │
```

---

## Port Configuration

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Frontend | 3000 | http://localhost:3000 | Next.js dev server |
| Backend API | 8000 | http://localhost:8000 | FastAPI server |
| API Docs | 8000 | http://localhost:8000/docs | Swagger UI |
| Firebase Emulator | 4000 | http://localhost:4000 | Firebase UI (optional) |
| Firestore Emulator | 8080 | http://localhost:8080 | Firestore (optional) |

---

This architecture provides a complete, secure, scalable foundation for your data preprocessing platform!
