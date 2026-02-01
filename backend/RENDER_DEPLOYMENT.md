# Render Deployment Guide for PrepIt Backend

## Prerequisites
- Render account (https://render.com)
- GitHub repository with your backend code
- Firebase project setup with credentials
- Supabase project setup with storage buckets

## Step 1: Prepare Your Repository

1. Ensure all changes are committed and pushed to GitHub:
```bash
git add .
git commit -m "Production-ready backend configuration"
git push origin main
```

2. Verify these files exist in your backend folder:
   - `requirements.txt`
   - `app/main.py`
   - `.env.example` (for reference)
   - `firebase-credentials.json` (will be configured as secret)

## Step 2: Create Web Service on Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

### Basic Settings
- **Name**: `prepit-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `backend` (if backend is in a subdirectory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Instance Type
- **Free** (for testing) or **Starter** (for production)

## Step 3: Environment Variables

Add all environment variables from `.env.example`:

### Required Variables:

#### Environment
```
ENVIRONMENT=production
```

#### Firebase Configuration
```
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
your-private-key-here
-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=your-service-account-email@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com
FIREBASE_WEB_API_KEY=your-firebase-web-api-key-here
```

#### Supabase Configuration
```
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_BUCKET_ORIGINALS=originals
SUPABASE_BUCKET_PROCESSED=processed
```

#### File Upload Configuration
```
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=csv,xlsx,xls
```

**Important Notes:**
- For `FIREBASE_PRIVATE_KEY`, preserve line breaks or use `\n` for newlines
- Keep quotes around the private key value
- Use "Secret Files" feature for `firebase-credentials.json` if needed

## Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Monitor the deployment logs for any errors

## Step 5: Verify Deployment

1. Once deployed, you'll get a URL like: `https://prepit-backend.onrender.com`
2. Test the endpoints:
   - `https://your-app.onrender.com/` - Should return API info
   - `https://your-app.onrender.com/health` - Should return health status
   - `https://your-app.onrender.com/docs` - API documentation (disabled in production by default)

## Step 6: Update Frontend

Update your frontend environment variables with the new backend URL:
```
REACT_APP_API_URL=https://your-app.onrender.com
```

Or for Next.js:
```
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
```

## Troubleshooting

### Common Issues:

#### 1. Build Fails
- Check `requirements.txt` for correct package names
- Verify Python version compatibility
- Check build logs for specific errors

#### 2. Application Won't Start
- Verify start command is correct
- Check that `PORT` environment variable is used correctly
- Review application logs

#### 3. CORS Errors
- Verify frontend URL is correct in CORS configuration
- Check that `ENVIRONMENT=production` is set
- Ensure frontend is deployed and accessible

#### 4. Firebase Connection Issues
- Verify all Firebase environment variables are set correctly
- Check that private key has proper line breaks
- Ensure Firebase project is active

#### 5. Supabase Storage Issues
- Verify Supabase URL and keys are correct
- Check that storage buckets exist and are public
- Ensure RLS policies are configured correctly

### Viewing Logs
- Go to your service dashboard on Render
- Click "Logs" tab to view real-time logs
- Use logs to diagnose connection or runtime issues

## Performance Optimization

### For Free Tier
- Service spins down after 15 minutes of inactivity
- First request after spin-down will be slow (cold start)
- Consider upgrading to Starter for always-on service

### For Production
1. **Upgrade to Starter or higher** for:
   - No spin-down
   - Better performance
   - Custom domains
   - More resources

2. **Enable health checks**:
   - Render will ping `/health` endpoint
   - Keeps service warm

3. **Monitor performance**:
   - Use Render metrics
   - Set up alerts for errors

## Security Checklist

- ✅ All sensitive data in environment variables
- ✅ CORS configured with specific origins
- ✅ API documentation disabled in production
- ✅ HTTPS enabled (automatic with Render)
- ✅ Environment set to `production`
- ✅ Firebase admin credentials secured
- ✅ Supabase keys secured

## Updating Your Application

To deploy updates:
1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```
2. Render automatically redeploys on push (if auto-deploy is enabled)
3. Monitor deployment in Render dashboard

## Rollback

If deployment fails:
1. Go to Render dashboard
2. Click "Rollback" button
3. Select previous successful deployment

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com
- Your Backend Health Check: `https://your-app.onrender.com/health`
