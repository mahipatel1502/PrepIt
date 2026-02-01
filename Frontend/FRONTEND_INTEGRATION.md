# 🎨 Frontend API Integration Guide

## ✅ What's Been Integrated

The Next.js frontend has been successfully connected to the FastAPI backend with complete authentication and file upload capabilities.

## 📦 New Files Created

### API Layer
- **[lib/api-config.ts](lib/api-config.ts)** - API configuration and endpoints
- **[lib/api-client.ts](lib/api-client.ts)** - API client with all backend methods
- **[.env.local](.env.local)** - Local environment variables
- **[.env.example](.env.example)** - Environment template

### Components & Hooks
- **[components/protected-route.tsx](components/protected-route.tsx)** - Route protection wrapper
- **[hooks/use-file-upload.ts](hooks/use-file-upload.ts)** - File upload hook with progress

### Updated Files
- **[context/auth-context.tsx](context/auth-context.tsx)** - Real API integration
- **[app/login/page.tsx](app/login/page.tsx)** - Backend authentication
- **[app/signup/page.tsx](app/signup/page.tsx)** - Backend user registration

## 🚀 Quick Start

### 1. Install Dependencies (if needed)
```bash
cd Frontend
pnpm install
# or npm install
```

### 2. Configure Environment
The `.env.local` file has been created with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Start Development Server
```bash
pnpm dev
# or npm run dev
```

Frontend will run on: `http://localhost:3000`

### 4. Ensure Backend is Running
```bash
cd ../backend
uvicorn app.main:app --reload
```

Backend should be on: `http://localhost:8000`

## 🔌 API Integration Details

### Authentication Context

The `AuthContext` now:
- ✅ Connects to real backend API
- ✅ Stores JWT tokens in localStorage
- ✅ Automatically loads user on page refresh
- ✅ Handles token expiration
- ✅ Provides loading states

**Usage:**
```tsx
import { useAuth } from "@/context/auth-context"

function MyComponent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth()
  
  if (isLoading) return <div>Loading...</div>
  
  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user.name}!</p>
      ) : (
        <button onClick={() => login(email, password)}>Login</button>
      )}
    </div>
  )
}
```

### API Client

The `apiClient` provides methods for all backend endpoints:

```typescript
import { apiClient } from "@/lib/api-client"

// Signup
const response = await apiClient.signup({
  full_name: "John Doe",
  email: "john@example.com",
  password: "SecurePass123"
})

// Login
const response = await apiClient.login({
  email: "john@example.com",
  password: "SecurePass123"
})

// Get current user
const user = await apiClient.getCurrentUser()

// Update user
const updated = await apiClient.updateUser({
  full_name: "John Smith"
})

// Change password
await apiClient.changePassword({
  old_password: "SecurePass123",
  new_password: "NewSecurePass456"
})

// Upload dataset
const result = await apiClient.uploadDataset(file)

// Logout
await apiClient.logout()
```

### File Upload Hook

Use the `useFileUpload` hook for easy file uploads:

```tsx
import { useFileUpload } from "@/hooks/use-file-upload"

function UploadComponent() {
  const { uploadFile, isUploading, uploadProgress, error } = useFileUpload()
  
  const handleUpload = async (file: File) => {
    try {
      const result = await uploadFile(file)
      console.log("Upload successful:", result)
    } catch (err) {
      console.error("Upload failed:", err)
    }
  }
  
  return (
    <div>
      {isUploading && (
        <div>Uploading... {uploadProgress?.percentage}%</div>
      )}
      {error && <div>Error: {error}</div>}
    </div>
  )
}
```

### Protected Routes

Wrap pages that require authentication:

```tsx
import ProtectedRoute from "@/components/protected-route"

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>Protected content here</div>
    </ProtectedRoute>
  )
}
```

## 🔐 Authentication Flow

### Signup Process
1. User fills signup form
2. Frontend validates input
3. Calls `apiClient.signup()` with user data
4. Backend creates user in Firebase
5. Backend returns JWT token + user info
6. Token stored in localStorage
7. User context updated
8. Redirect to dashboard

### Login Process
1. User enters credentials
2. Frontend validates input
3. Calls `apiClient.login()` with credentials
4. Backend verifies password
5. Backend returns JWT token + user info
6. Token stored in localStorage
7. User context updated
8. Redirect to dashboard

### Auto-Login (on page refresh)
1. AuthProvider checks localStorage for token
2. If token exists, calls `apiClient.getCurrentUser()`
3. If valid, user context updated
4. If invalid, token removed and user stays logged out

### Protected Route Access
1. User navigates to protected page
2. ProtectedRoute checks `isAuthenticated`
3. If not authenticated, redirect to `/login`
4. If authenticated, render page content

## 🎯 Features Implemented

### ✅ Authentication
- [x] User registration (signup)
- [x] User login
- [x] Auto-login on page refresh
- [x] JWT token management
- [x] User context available globally
- [x] Logout functionality
- [x] Protected routes

### ✅ Error Handling
- [x] API error messages displayed
- [x] Network error handling
- [x] Token expiration handling
- [x] Form validation errors

### ✅ Loading States
- [x] Loading spinner during auth
- [x] Loading states for API calls
- [x] Upload progress indication
- [x] Skeleton loaders where needed

### ✅ User Experience
- [x] Persistent sessions (localStorage)
- [x] Automatic redirects
- [x] Error messages to users
- [x] Success feedback

## 📋 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | ✅ Yes | `http://localhost:8000` |

### Development
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## 🔧 API Response Types

### AuthResponse
```typescript
{
  access_token: string
  token_type: "bearer"
  user: {
    user_id: string
    full_name: string
    email: string
    created_at: string
  }
}
```

### User
```typescript
{
  id: string
  email: string
  name: string
  provider: "email" | "google"
  createdAt?: string
}
```

### Upload Result
```typescript
{
  message: string
  user_id: string
  preprocessing_report: {
    missing_values: number
    duplicate_rows: number
    cleaned_rows: number
  }
  analytics: {
    row_count: number
    column_count: number
  }
}
```

## 🚨 Common Issues & Solutions

### Issue: "Network error. Please check your connection."
**Solution:**
- Ensure backend is running on `http://localhost:8000`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Verify CORS is enabled in backend

### Issue: "401 Unauthorized" on protected routes
**Solution:**
- Token may have expired (30 min default)
- Login again to get new token
- Check token is being sent in Authorization header

### Issue: Login works but page refresh logs out
**Solution:**
- Check browser localStorage has `prepit_auth_token`
- Check browser console for errors
- Verify `getCurrentUser()` is being called on mount

### Issue: CORS errors in browser console
**Solution:**
- Backend CORS middleware should allow your frontend origin
- In backend `main.py`, ensure CORS settings include frontend URL
- For dev: `allow_origins=["http://localhost:3000"]`

## 🧪 Testing the Integration

### 1. Test Signup
```bash
# Frontend: http://localhost:3000/signup
1. Fill in name, email, password
2. Click "Create account"
3. Should redirect to /dashboard
4. Check browser localStorage for token
```

### 2. Test Login
```bash
# Frontend: http://localhost:3000/login
1. Enter email and password
2. Click "Sign in"
3. Should redirect to /dashboard
4. Check browser localStorage for token
```

### 3. Test Protected Route
```bash
# Without login
1. Go to http://localhost:3000/dashboard
2. Should redirect to /login

# With login
1. Login first
2. Go to http://localhost:3000/dashboard
3. Should show dashboard content
```

### 4. Test Auto-Login
```bash
1. Login to the app
2. Refresh the page (F5)
3. Should remain logged in
4. Check Network tab for GET /api/auth/me
```

### 5. Test Logout
```bash
1. Click logout button
2. Should redirect to home/login
3. localStorage token should be removed
4. Trying to access /dashboard should redirect to /login
```

### 6. Test File Upload (once logged in)
```bash
1. Go to upload page
2. Select a CSV/Excel file
3. Should see upload progress
4. Should receive processing results from backend
```

## 📱 Using the API in Components

### Example: User Profile Component
```tsx
"use client"

import { useAuth } from "@/context/auth-context"
import { apiClient } from "@/lib/api-client"
import { useState } from "react"

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [name, setName] = useState(user?.name || "")
  const [loading, setLoading] = useState(false)

  const handleUpdate = async () => {
    setLoading(true)
    try {
      await apiClient.updateUser({ full_name: name })
      await refreshUser() // Refresh user context
      alert("Profile updated!")
    } catch (error: any) {
      alert(error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Profile</h1>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <button onClick={handleUpdate} disabled={loading}>
        {loading ? "Updating..." : "Update Profile"}
      </button>
    </div>
  )
}
```

### Example: Dataset Upload Component
```tsx
"use client"

import { useFileUpload } from "@/hooks/use-file-upload"

export default function UploadComponent() {
  const { uploadFile, isUploading, uploadProgress, error } = useFileUpload()
  
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    try {
      const result = await uploadFile(file)
      console.log("Processing results:", result)
      alert(`File processed! ${result.analytics.row_count} rows`)
    } catch (err) {
      console.error("Upload failed:", err)
    }
  }
  
  return (
    <div>
      <input type="file" onChange={handleFileChange} accept=".csv,.xlsx" />
      
      {isUploading && (
        <div>
          <p>Uploading... {uploadProgress?.percentage}%</p>
          <progress value={uploadProgress?.percentage} max="100" />
        </div>
      )}
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  )
}
```

## 🎨 Next Steps

### Recommended Enhancements

1. **Add Protected Route Wrappers**
   - Wrap dashboard, upload, profile pages with `<ProtectedRoute>`

2. **Implement Password Reset**
   - Add "Forgot Password" flow
   - Email verification

3. **Add Loading Skeletons**
   - Better UX during data fetching
   - Smooth transitions

4. **Implement Refresh Tokens**
   - Longer session duration
   - Auto-refresh before expiry

5. **Add Error Boundary**
   - Catch and display API errors gracefully

6. **Implement Optimistic Updates**
   - Update UI before API confirmation
   - Revert on error

7. **Add Request Caching**
   - Cache user data
   - Reduce API calls

8. **Implement File Upload Progress**
   - Real upload progress bar
   - Cancel upload functionality

## 📚 Additional Resources

- **Backend API Docs**: `http://localhost:8000/docs`
- **Backend Setup**: `../backend/AUTH_SETUP.md`
- **API Reference**: `../backend/API_REFERENCE.md`

## ✨ Summary

Your Next.js frontend is now fully connected to the FastAPI backend with:

✅ Complete authentication system
✅ JWT token management
✅ Protected routes
✅ File upload capability
✅ Error handling
✅ Loading states
✅ Auto-login on refresh
✅ User context throughout app

**You're ready to build!** Start both servers and test the full authentication flow.
