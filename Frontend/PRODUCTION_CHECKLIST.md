# Production Deployment Checklist

## Pre-Deployment

### Code Quality
- [ ] All TypeScript errors resolved (`pnpm build` runs successfully)
- [ ] No console errors in browser
- [ ] All imports are correct
- [ ] No unused dependencies

### Testing
- [ ] Test all authentication flows (signup, login, Google sign-in, logout)
- [ ] Test file upload functionality
- [ ] Test dashboard data display
- [ ] Test history page
- [ ] Test profile/settings page
- [ ] Test on different browsers (Chrome, Firefox, Safari, Edge)
- [ ] Test on mobile devices (responsive design)
- [ ] Test dark/light theme switching

### Security
- [ ] `.env.local` is in `.gitignore`
- [ ] No sensitive data in code
- [ ] Firebase API keys are restricted (optional but recommended)
- [ ] CORS configured properly in backend

### Configuration Files
- [ ] `next.config.mjs` - Production settings configured
- [ ] `vercel.json` - Deployment settings ready
- [ ] `.env.example` - Updated with all required variables
- [ ] `.nvmrc` - Node version specified
- [ ] `README.md` - Instructions clear
- [ ] `DEPLOYMENT.md` - Deployment guide complete

## Backend Preparation

### Backend Deployment
- [ ] Backend deployed and accessible via HTTPS
- [ ] Backend API URL noted (e.g., https://api.prepit.com)
- [ ] CORS configured to allow Vercel domains:
  ```python
  origins = [
      "https://*.vercel.app",
      "https://your-app.vercel.app",
      "https://your-custom-domain.com",  # if applicable
  ]
  ```
- [ ] Backend health check endpoint working
- [ ] All API endpoints tested with HTTPS

### Database & Storage
- [ ] Firebase Storage configured
- [ ] Database accessible from backend
- [ ] Backup strategy in place

## Firebase Configuration

### Firebase Console
- [ ] Go to [Firebase Console](https://console.firebase.google.com)
- [ ] Select your project (prepit-200)
- [ ] Authentication → Settings → Authorized domains
  - [ ] Add `your-app.vercel.app`
  - [ ] Add `*.vercel.app` for preview deployments
  - [ ] Add custom domain if applicable
- [ ] Copy all Firebase credentials ready for Vercel

### Google OAuth Setup
- [ ] Go to [Google Cloud Console](https://console.cloud.google.com)
- [ ] Navigate to APIs & Services → Credentials
- [ ] Edit OAuth 2.0 Client ID
- [ ] Add authorized redirect URIs:
  - [ ] `https://your-app.vercel.app`
  - [ ] `https://prepit-200.firebaseapp.com/__/auth/handler`
  - [ ] Any custom domains

## Vercel Deployment

### Initial Setup
- [ ] Sign up/Log in to [Vercel](https://vercel.com)
- [ ] Connect GitHub/GitLab/Bitbucket account
- [ ] Import repository

### Project Configuration
- [ ] Framework: Next.js (auto-detected)
- [ ] Root Directory: `Frontend` (or `.` if frontend is root)
- [ ] Build Command: `pnpm build`
- [ ] Output Directory: `.next`
- [ ] Install Command: `pnpm install`
- [ ] Node.js Version: 18.x

### Environment Variables in Vercel

Add these in Project Settings → Environment Variables:

#### Backend
- [ ] `NEXT_PUBLIC_API_URL` = `https://your-backend-api.com`

#### Firebase (copy from .env.local)
- [ ] `NEXT_PUBLIC_FIREBASE_API_KEY`
- [ ] `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- [ ] `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- [ ] `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- [ ] `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- [ ] `NEXT_PUBLIC_FIREBASE_APP_ID`

**Important:** Set these for all environments (Production, Preview, Development)

### Deploy
- [ ] Trigger deployment (push to main branch or click deploy)
- [ ] Wait for build to complete
- [ ] Check build logs for errors

## Post-Deployment Verification

### Basic Functionality
- [ ] Homepage loads correctly
- [ ] No console errors in browser
- [ ] Images load properly
- [ ] Navigation works

### Authentication
- [ ] Email signup works
- [ ] Email login works
- [ ] Google sign-in works
- [ ] Logout works
- [ ] Protected routes redirect to login
- [ ] Token persistence works (refresh page stays logged in)

### Core Features
- [ ] File upload works
- [ ] File processing completes
- [ ] Dashboard displays data correctly
- [ ] Charts render properly
- [ ] History page loads records
- [ ] File download works
- [ ] Delete functionality works

### API Integration
- [ ] All API calls succeed
- [ ] Error handling works
- [ ] Loading states display correctly
- [ ] Success messages show
- [ ] Error messages are clear

### Performance
- [ ] Page load time < 3 seconds
- [ ] Images are optimized
- [ ] No layout shifts
- [ ] Smooth animations
- [ ] Check Lighthouse score (aim for 90+)

### Cross-Browser Testing
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

### Mobile Testing
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] Responsive design works
- [ ] Touch interactions work
- [ ] No horizontal scrolling

### SEO & Metadata
- [ ] Page titles correct
- [ ] Meta descriptions set
- [ ] Favicon appears
- [ ] Open Graph tags (if needed)

## Domain Setup (if using custom domain)

- [ ] Add domain in Vercel
- [ ] Configure DNS records
- [ ] Wait for DNS propagation
- [ ] Verify SSL certificate
- [ ] Add domain to Firebase authorized domains
- [ ] Update CORS in backend
- [ ] Test with custom domain

## Monitoring & Maintenance

### Analytics
- [ ] Vercel Analytics enabled
- [ ] Google Analytics configured (if needed)
- [ ] Error tracking setup (optional: Sentry)

### Ongoing Monitoring
- [ ] Check Vercel deployment logs regularly
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review user feedback

### Backup & Rollback Plan
- [ ] Know how to rollback in Vercel (Deployments → Promote to Production)
- [ ] Keep previous deployment available
- [ ] Database backup strategy in place

## Documentation

- [ ] Update README with production URL
- [ ] Document any production-specific configurations
- [ ] Share deployment guide with team
- [ ] Document environment variables

## Final Checks

- [ ] All team members can access Vercel project
- [ ] Environment variables documented
- [ ] Emergency contacts listed
- [ ] Rollback procedure tested
- [ ] Success! 🎉

## Troubleshooting Quick Reference

### Build Fails
1. Check TypeScript errors: `pnpm build` locally
2. Verify all dependencies installed
3. Check Vercel build logs

### Google Sign-In Fails
1. Verify domain in Firebase authorized domains
2. Check redirect URIs in Google Cloud Console
3. Verify Firebase credentials in Vercel env vars

### API Calls Fail
1. Check `NEXT_PUBLIC_API_URL` is correct
2. Verify backend CORS settings
3. Check backend is running and accessible
4. Inspect network tab in browser

### Environment Variables Not Working
1. Ensure they start with `NEXT_PUBLIC_`
2. Redeploy after adding env vars
3. Check they're set for correct environment

## Support Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Firebase Console](https://console.firebase.google.com)
- [Vercel Support](https://vercel.com/support)

---

**Date Created**: February 2026
**Last Updated**: February 2026
