# PrepIt Frontend - Vercel Deployment Guide

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- Backend API deployed and accessible via HTTPS
- Firebase project configured with web app

## Deployment Steps

### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### 2. Prepare Firebase for Production

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project (prepit-200)
3. Click on "Project Settings" → "General"
4. Under "Your apps", find your web app
5. Add your production domain to **Authorized domains**:
   - Go to "Authentication" → "Settings" → "Authorized domains"
   - Add your Vercel domain: `your-app.vercel.app`
   - Also add any custom domains you plan to use

### 3. Connect to Vercel

#### Option A: Deploy via Vercel Dashboard (Recommended)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your Git repository
4. Configure project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `Frontend` (if monorepo) or `./`
   - **Build Command**: `pnpm build` (or `npm run build`)
   - **Output Directory**: `.next`
   - **Install Command**: `pnpm install` (or `npm install`)

#### Option B: Deploy via CLI

```bash
cd Frontend
vercel
```

Follow the prompts to link your project.

### 4. Configure Environment Variables in Vercel

Go to your project settings in Vercel Dashboard → "Environment Variables" and add:

#### Required Variables:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-backend-api.com` | Your production backend URL |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Your API key | From Firebase Console |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | `prepit-200.firebaseapp.com` | Your Firebase auth domain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | `prepit-200` | Your Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | `prepit-200.appspot.com` | Your Firebase storage bucket |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Your sender ID | From Firebase Console |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Your app ID | From Firebase Console |

**Important:** 
- Make sure to add these variables for all environments (Production, Preview, Development)
- You can copy these from your `.env.local` file
- Keep the Firebase credentials the same (they're already configured for your domain)

### 5. Update Backend CORS Settings

Update your backend to allow requests from your Vercel domain:

```python
# In your backend's main.py or app.py
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel domain
    "https://*.vercel.app",  # Allow all preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Deploy

#### Via Dashboard:
- Push your code to GitHub
- Vercel will automatically deploy on every push to main branch

#### Via CLI:
```bash
# Production deployment
vercel --prod

# Preview deployment
vercel
```

### 7. Post-Deployment Verification

Test the following features:
- ✅ Homepage loads correctly
- ✅ Google Sign-In works
- ✅ Email/Password authentication works
- ✅ File upload functions
- ✅ Dashboard displays data
- ✅ API calls succeed
- ✅ Protected routes redirect correctly

## Custom Domain Setup (Optional)

1. Go to Project Settings → "Domains"
2. Add your custom domain
3. Update DNS records as instructed
4. Add custom domain to Firebase authorized domains
5. Update CORS in backend to include custom domain

## Automatic Deployments

Vercel automatically deploys:
- **Production**: Every push to `main` branch → `your-app.vercel.app`
- **Preview**: Every push to other branches → `your-app-{branch}.vercel.app`

## Environment-Specific URLs

- **Production**: `https://your-app.vercel.app`
- **Preview**: `https://your-app-git-{branch}-{team}.vercel.app`
- **Development**: `http://localhost:3000`

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Ensure all environment variables are set
- Verify TypeScript has no errors: `pnpm run build` locally

### Google Sign-In Not Working
- Verify domain is added to Firebase authorized domains
- Check that Firebase credentials are correctly set in Vercel
- Ensure redirect URIs match in Google Cloud Console

### API Calls Failing
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend CORS settings include Vercel domain
- Ensure backend is accessible via HTTPS
- Check browser console for specific errors

### 502/504 Errors
- Check if backend is running and accessible
- Verify backend URL in environment variables
- Check Vercel function logs

## Performance Optimization

The following optimizations are already configured:

✅ Image optimization enabled for production
✅ TypeScript strict mode enabled
✅ SWC minification enabled
✅ Compression enabled
✅ Security headers configured
✅ Package imports optimized

## Monitoring

1. **Vercel Analytics**: Automatically enabled for your deployment
2. **Error Tracking**: Check Vercel logs for runtime errors
3. **Build Logs**: Available in deployment details

## Rollback

If something goes wrong:

1. Go to Deployments tab in Vercel Dashboard
2. Find the last working deployment
3. Click "..." → "Promote to Production"

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Firebase Hosting Guide](https://firebase.google.com/docs/hosting)

---

**Last Updated**: February 2026
**Next.js Version**: 16.0.10
**Node Version Required**: 18.x or higher
