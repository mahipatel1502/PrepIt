# Firebase Environment Variables - Quick Reference

## 🚀 Quick Setup

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Get credentials from Firebase Console:**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Project Settings → Service Accounts → Generate New Private Key
   - Download JSON file

3. **Copy values from JSON to .env:**
   ```env
   FIREBASE_TYPE=service_account                    # from "type"
   FIREBASE_PROJECT_ID=your-project-id             # from "project_id"
   FIREBASE_PRIVATE_KEY_ID=your-key-id             # from "private_key_id"
   FIREBASE_PRIVATE_KEY="-----BEGIN..."           # from "private_key" (escape \n)
   FIREBASE_CLIENT_EMAIL=xxx@xxx.iam...            # from "client_email"
   FIREBASE_CLIENT_ID=123456789                    # from "client_id"
   FIREBASE_CLIENT_CERT_URL=https://...            # from "client_x509_cert_url"
   FIREBASE_WEB_API_KEY=AIzaSy...                  # from Project Settings → General
   ```

4. **Start server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📋 Environment Variables Reference

| Variable | Source | Required | Example |
|----------|--------|----------|---------|
| `FIREBASE_TYPE` | JSON: `type` | ✅ Yes | `service_account` |
| `FIREBASE_PROJECT_ID` | JSON: `project_id` | ✅ Yes | `my-project-123` |
| `FIREBASE_PRIVATE_KEY_ID` | JSON: `private_key_id` | ✅ Yes | `a1b2c3d4e5...` |
| `FIREBASE_PRIVATE_KEY` | JSON: `private_key` | ✅ Yes | `"-----BEGIN PRIVATE KEY-----\n..."` |
| `FIREBASE_CLIENT_EMAIL` | JSON: `client_email` | ✅ Yes | `firebase-adminsdk@....iam.gserviceaccount.com` |
| `FIREBASE_CLIENT_ID` | JSON: `client_id` | ✅ Yes | `123456789012345678901` |
| `FIREBASE_AUTH_URI` | JSON: `auth_uri` | ❌ No | `https://accounts.google.com/o/oauth2/auth` |
| `FIREBASE_TOKEN_URI` | JSON: `token_uri` | ❌ No | `https://oauth2.googleapis.com/token` |
| `FIREBASE_AUTH_PROVIDER_CERT_URL` | JSON: `auth_provider_x509_cert_url` | ❌ No | `https://www.googleapis.com/oauth2/v1/certs` |
| `FIREBASE_CLIENT_CERT_URL` | JSON: `client_x509_cert_url` | ❌ No | `https://www.googleapis.com/robot/v1/metadata/x509/...` |
| `FIREBASE_UNIVERSE_DOMAIN` | JSON: `universe_domain` | ❌ No | `googleapis.com` |
| `FIREBASE_WEB_API_KEY` | Console: Project Settings → General | ✅ Yes | `AIzaSyCnrl0zCCGgA4kJdC...` |

## ⚠️ Important: Private Key Format

The private key **must** have escaped newlines in `.env`:

### ❌ Wrong (will fail):
```env
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkq...
-----END PRIVATE KEY-----"
```

### ✅ Correct:
```env
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkq...\n-----END PRIVATE KEY-----\n"
```

**Note:** Each `\n` in JSON becomes `\\n` in `.env` file

## 🔍 Verification

Check if setup is correct:

```bash
# Test that all required variables are set
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
required = ['FIREBASE_TYPE', 'FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY_ID', 
            'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL', 'FIREBASE_CLIENT_ID', 
            'FIREBASE_WEB_API_KEY']
missing = [v for v in required if not os.getenv(v)]
if missing:
    print(f'❌ Missing: {missing}')
else:
    print('✅ All required variables set!')
"
```

## 🐛 Common Issues

### Issue: "Missing required Firebase environment variables"
**Solution:** Check that all required variables are in `.env` and spelled correctly

### Issue: "Failed to initialize Firebase"
**Solution:** Verify `FIREBASE_PRIVATE_KEY` has escaped newlines (`\\n` not `\n`)

### Issue: "Invalid credentials"
**Solution:** 
- Ensure credentials are from correct Firebase project
- Re-download service account key from Firebase Console
- Check for extra spaces or quotes in variable values

### Issue: ".env file not found"
**Solution:** 
```bash
cp .env.example .env
# Then add your credentials
```

## 📝 Example .env File

```env
# Firebase Service Account Configuration
FIREBASE_TYPE=service_account
FIREBASE_PROJECT_ID=prepit-200
FIREBASE_PRIVATE_KEY_ID=61b12cfe3ea707341a2b21028fdb72b30536d77b
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC0J/1OjxS1rngi\nUM9/Ugg8zZYOh8o67ldKchsuYP2EZlQFG16tRH4KNwY6Qy5R9/LOuwhzJwECVoTB\nbN3m+LehxRHDhTFl0rcEfDvnkoWzf6B5UnaPxosPibRFSiZmH41SvwCBCF9icIF4\nPjOCpzQuzc4gQ0ZeAeLDUNn1krFe41bm+kL399ZbCm0NXG+KLCvOIgsgsRpbwheh\nHI1OLWHq/u6/fwAJWV+2ztLHeIvCZ5MFkx6kPH6kFr+9ZGkvJzcEgORuwiEG3LJR\nyKYY0rsN++XoXo4Y9PZqlmgZn9voeQz+8jLa/iMORG/Qhhlw1/y7RfWXwoPHJXue\nwBZZ9el7AgMBAAECggEAOUwUpKUd/ZCBNczEyaYh55CtPm7Skz6VdaBn467GQpM2\n+q7TREEp4v7QFLykIT6+MyDKFbGcgQ1aSJhi1OBaqvEd7rTQWqWTPrJybPqtWkLn\nm15uRdjsBmOR+Y2VO9qiHGSR+PfcOlc03jTONioOjyo2eg1bdm+cGul+gLuIfPhA\nS88ykEOHaSvIDSbpPwcG5Ue/JgowkjisndKQEpCDz7cAwfBOqip7ELU8wptjBYi+\nPQmv4cX1QasWvrIbh+7hw1SYcSk4rbrS1i1lQqERf5unZBuz/Og4jLXJvR/3yinY\nimZ6g1jQ9z2F9WiRArRNJHfZPWMn7iHyKDj6IRfFSQKBgQDzqeDEdWytGu+IDymn\nzX4QWAdmcQPD1ekkaOQWz0dwF9g6PjxmWKh3sHcX5aalUwkDCP9496gdTZ2pSC2L\nPzvn3QRbcXw9nFKekw/9YgiylikUXl3WIs2/e3gPEdY4JtXh7dPvD5K+N1fTJake\nt3nhtQwbtcPLCXpsK1RnrKCbOQKBgQC9Rv4pgbN+O7liilrdIg7+rLhsyx+MB852\nloaXCpxxychE4wMIl0WKVESv6PjuRy+AJtPoWPWkHQ53/Fx3LFK6OFOrZn9A4G8v\nUwFZ0fvRDj1HaZPAX5RQ8SpdyN1JKabq+fEccGZPu3MV0WdhUxwkCsnyexK06uqo\nvyTJSQJGUwKBgHBGWLFtwhPJk5HIGtOdVndFeLN1Y9y7FmCWjHMOM8as1g+QWdh3\nBbmQ8G9sfGs1ZbOmU8FzrF1ERF+aSJIfIwVly/ouwqbI/zDeZsHEiGlx05/1E5v2\nEYQn6lxXRbQ+ANPH+J3xORa4/Zjng5QJyvl7qQajrIJD7csl9BCJdL/RAoGAAfAb\nJBOm4dD8ueyOt5rkqmjcTojZ3tYpn/80i5FZPrUBLutgGZNq69qnBWIOQmpKKza6\njrNyeGavwjy8OaAjjLKM8MFQ5jomCUcBSYkj2eUabYPANoUEALwnYeRvl5MsmVVL\nya3A7moN6JhHRbDTJe9SWAA4lc+d7XJfjwwHUO8CgYBBrZ9LNLVxHh7Z/P5dXHlF\nQB77rP6uci/pq4xfPXlUH5yCzPqfDgf5MCB08H+vBsPYKOItNoW/XWBsjFJD4+Zu\n0AhKpNCa91zDw/Oy9IkfAuAewjndQMm0iDObQKkwwt0OqbmB1k2GlOvgAQiOWg8Z\njDzu9mvudE2lMaGAKQl/Mw==\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@prepit-200.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=115879772630145817127
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40prepit-200.iam.gserviceaccount.com
FIREBASE_UNIVERSE_DOMAIN=googleapis.com

# Firebase Web API Key
FIREBASE_WEB_API_KEY="AIzaSyCnrl0zCCGgA4kJdCW1435fPwaFQT_ZwmQ"

# Environment
ENVIRONMENT=development
```

## 🚀 Deployment

### Heroku
```bash
heroku config:set FIREBASE_TYPE=service_account
heroku config:set FIREBASE_PROJECT_ID=your-project-id
heroku config:set FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
# ... set all other variables
```

### Docker
```yaml
# docker-compose.yml
environment:
  - FIREBASE_TYPE=service_account
  - FIREBASE_PROJECT_ID=${FIREBASE_PROJECT_ID}
  - FIREBASE_PRIVATE_KEY=${FIREBASE_PRIVATE_KEY}
  # ... other variables
```

### AWS/Azure
Set environment variables in your app configuration dashboard or CLI.

---

**Need help?** Check [ENV_MIGRATION_SUMMARY.md](ENV_MIGRATION_SUMMARY.md) for detailed migration guide.
