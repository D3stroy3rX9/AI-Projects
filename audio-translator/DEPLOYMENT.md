# Audio Auto-Translator - Deployment Guide

Complete guide for deploying the Audio Auto-Translator to production.

---

## Table of Contents

1. [Overview](#overview)
2. [Backend Deployment (Railway/Render)](#backend-deployment)
3. [Frontend Deployment (Vercel)](#frontend-deployment)
4. [Database Setup](#database-setup)
5. [Environment Variables](#environment-variables)
6. [Domain Configuration](#domain-configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Overview

### Architecture

```
┌─────────────┐     HTTPS     ┌──────────────┐
│   Vercel    │ ◄────────────► │   Railway    │
│  (Frontend) │                │  (Backend)   │
└─────────────┘                └──────┬───────┘
                                      │
                                      ▼
                               ┌──────────────┐
                               │  PostgreSQL  │
                               │  (Database)  │
                               └──────────────┘
```

### Cost Estimate

**Development (Free Tier):**
- Frontend: Vercel (Free)
- Backend: Railway ($5/month credit, usually sufficient)
- Database: Railway PostgreSQL (included)
- **Total: $0-5/month**

**Alternative (Fully Free):**
- Frontend: Vercel (Free)
- Backend: Render (750 hours/month free)
- Database: Render PostgreSQL (90 days free, then paid)
- **Total: $0/month (with limitations)**

---

## Backend Deployment

### Option 1: Railway (Recommended)

Railway offers the best Python/FastAPI support with automatic deployments.

#### Step 1: Prepare the Backend

1. **Create Dockerfile** in `apps/api/`:

```dockerfile
# apps/api/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Whisper model during build (reduces startup time)
RUN python -c "import whisper; whisper.load_model('base')"

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Create `.dockerignore`** in `apps/api/`:

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
*.db
*.sqlite
.env
.env.local
tests/
*.pytest_cache
.coverage
```

#### Step 2: Deploy to Railway

1. **Sign up for Railway:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Select your repository
   - Choose `apps/api` as the root directory

3. **Configure Build Settings:**
   - Railway auto-detects Dockerfile
   - No additional configuration needed

4. **Add PostgreSQL:**
   - In your project, click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway provisions a PostgreSQL instance

5. **Set Environment Variables:**
   - Go to "Variables" tab
   - Add the following:

```env
DATABASE_URL=${{Postgres.DATABASE_URL}}
WHISPER_MODEL=base
TRANSLATION_BACKEND=libretranslate
LIBRETRANSLATE_URL=https://libretranslate.de
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

6. **Deploy:**
   - Railway automatically deploys on git push
   - Get your backend URL: `https://your-app.up.railway.app`

#### Step 3: Run Migrations

```bash
# Connect to Railway database
railway run alembic upgrade head
```

---

### Option 2: Render

Render offers 750 free hours per month, perfect for hobby projects.

#### Step 1: Create render.yaml

Create `render.yaml` in project root:

```yaml
services:
  # FastAPI Backend
  - type: web
    name: audio-translator-api
    runtime: python
    buildCommand: pip install -r apps/api/requirements.txt && python apps/api/download_models.py --model base
    startCommand: cd apps/api && uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: audio-translator-db
          property: connectionString
      - key: WHISPER_MODEL
        value: base
      - key: TRANSLATION_BACKEND
        value: libretranslate
      - key: LIBRETRANSLATE_URL
        value: https://libretranslate.de
      - key: CORS_ORIGINS
        value: https://your-vercel-app.vercel.app

databases:
  - name: audio-translator-db
    databaseName: audio_translator
    user: translator
```

#### Step 2: Deploy to Render

1. **Sign up for Render:**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Service:**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render reads `render.yaml` automatically

3. **Deploy:**
   - Click "Apply"
   - Render builds and deploys your app
   - Get your URL: `https://your-app.onrender.com`

---

## Frontend Deployment

### Vercel (Recommended)

Vercel is purpose-built for Next.js with zero-config deployments.

#### Step 1: Prepare Frontend

1. **Update API URLs** in `apps/web/.env.production`:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend-url.railway.app/ws/translate
```

2. **Update `package.json`** build script (if needed):

```json
{
  "scripts": {
    "build": "next build",
    "start": "next start"
  }
}
```

#### Step 2: Deploy to Vercel

1. **Sign up for Vercel:**
   - Go to https://vercel.com
   - Sign up with GitHub

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select `apps/web` as root directory

3. **Configure Build Settings:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `apps/web`
   - **Build Command:** `pnpm build` (or `npm run build`)
   - **Output Directory:** `.next`

4. **Set Environment Variables:**
   - Add the following in Vercel dashboard:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend-url.railway.app/ws/translate
```

5. **Deploy:**
   - Click "Deploy"
   - Vercel builds and deploys automatically
   - Get your URL: `https://your-app.vercel.app`

#### Step 3: Update Backend CORS

Update backend `CORS_ORIGINS` environment variable:

```env
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

This allows both production and preview deployments.

---

## Database Setup

### Railway PostgreSQL

Railway provisions PostgreSQL automatically. No setup needed!

**Connection Details:**
- Accessible via `DATABASE_URL` environment variable
- Automatic backups
- Point-in-time recovery

### Render PostgreSQL

Render provides 90 days free PostgreSQL.

**After 90 days:**
- Upgrade to paid plan ($7/month)
- Or migrate to another provider (Supabase, Neon)

### Running Migrations

**Locally:**
```bash
cd apps/api
alembic upgrade head
```

**On Railway:**
```bash
railway run alembic upgrade head
```

**On Render:**
```bash
# Use Render shell
alembic upgrade head
```

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Whisper Model
WHISPER_MODEL=base  # Options: tiny, base, small, medium

# Translation
TRANSLATION_BACKEND=libretranslate
LIBRETRANSLATE_URL=https://libretranslate.de

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app

# Optional
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
```

### Frontend (.env.production)

```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/ws/translate
```

---

## Domain Configuration

### Custom Domain on Vercel

1. **Add Domain:**
   - Go to Project Settings → Domains
   - Add your custom domain (e.g., `translator.example.com`)
   - Follow DNS configuration instructions

2. **DNS Configuration:**
   - Add CNAME record: `translator` → `cname.vercel-dns.com`
   - Or A record: `@` → Vercel's IP

3. **HTTPS:**
   - Vercel automatically provisions SSL certificate
   - Usually takes 2-5 minutes

### Custom Domain on Railway

1. **Add Domain:**
   - Go to Settings → Networking
   - Click "Generate Domain" or "Custom Domain"
   - Add your domain (e.g., `api.example.com`)

2. **DNS Configuration:**
   - Add CNAME record: `api` → `your-app.up.railway.app`

3. **Update Frontend:**
   - Update `NEXT_PUBLIC_API_URL` to use custom domain

---

## Monitoring & Logging

### Railway Monitoring

1. **Access Logs:**
   - Click on your service
   - Go to "Deployments" → Select deployment
   - View real-time logs

2. **Metrics:**
   - CPU usage
   - Memory usage
   - Network traffic

### Render Monitoring

1. **Logs:**
   - Go to service dashboard
   - Click "Logs" tab
   - Filter by severity

2. **Metrics:**
   - Available in paid plans
   - CPU, memory, requests/sec

### Application Monitoring (Optional)

**Sentry (Error Tracking):**
```python
# Install: pip install sentry-sdk
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

**LogRocket (Session Replay):**
```javascript
// Frontend monitoring
import LogRocket from 'logrocket';
LogRocket.init('your-app-id');
```

---

## Performance Optimization

### Backend

1. **Enable Gzip Compression:**
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

2. **Connection Pooling:**
```python
# Already configured in database.py
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True
)
```

3. **Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/translate")
@limiter.limit("10/minute")
async def translate():
    pass
```

### Frontend

1. **Enable Next.js Production Optimizations:**
   - Already enabled by default in production build
   - Code splitting, tree shaking, minification

2. **Image Optimization:**
   - Use Next.js `<Image>` component
   - Automatic WebP conversion
   - Lazy loading

3. **Caching:**
   - Static assets cached automatically by Vercel
   - API responses cached with SWR

---

## Troubleshooting

### Backend Issues

**Issue: WebSocket connections failing**
- **Cause:** CORS or WebSocket protocol mismatch
- **Solution:** Ensure `CORS_ORIGINS` includes frontend URL
- **Solution:** Use `wss://` (not `ws://`) for HTTPS backends

**Issue: Whisper model not loading**
- **Cause:** Insufficient memory or slow startup
- **Solution:** Pre-download model in Dockerfile
- **Solution:** Use smaller model (`tiny` instead of `base`)

**Issue: Database connection errors**
- **Cause:** Wrong connection string or network issue
- **Solution:** Verify `DATABASE_URL` is correct
- **Solution:** Check database is running and accessible

**Issue: 502 Bad Gateway**
- **Cause:** Backend crashed or didn't start
- **Solution:** Check logs for startup errors
- **Solution:** Verify all dependencies installed correctly

### Frontend Issues

**Issue: API calls failing**
- **Cause:** Wrong API URL or CORS issue
- **Solution:** Verify `NEXT_PUBLIC_API_URL` is correct
- **Solution:** Check browser console for CORS errors

**Issue: WebSocket not connecting**
- **Cause:** Wrong WebSocket URL
- **Solution:** Use `wss://` for HTTPS (not `ws://`)
- **Solution:** Verify backend WebSocket endpoint is accessible

**Issue: Build failures on Vercel**
- **Cause:** Missing dependencies or build errors
- **Solution:** Check build logs in Vercel dashboard
- **Solution:** Test build locally: `pnpm build`

**Issue: Environment variables not working**
- **Cause:** Forgot `NEXT_PUBLIC_` prefix
- **Solution:** All client-side env vars must start with `NEXT_PUBLIC_`
- **Solution:** Redeploy after adding env vars

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass locally
- [ ] Environment variables documented
- [ ] Database migrations created
- [ ] Dockerfile tested locally
- [ ] CORS configured correctly
- [ ] API endpoints documented

### Backend Deployment

- [ ] Railway/Render project created
- [ ] PostgreSQL database provisioned
- [ ] Environment variables configured
- [ ] Dockerfile builds successfully
- [ ] Migrations run successfully
- [ ] Health check endpoint accessible
- [ ] WebSocket connections working

### Frontend Deployment

- [ ] Vercel project created
- [ ] Build succeeds
- [ ] Environment variables set
- [ ] API URL points to backend
- [ ] WebSocket URL correct (wss://)
- [ ] PWA manifest accessible
- [ ] All pages load correctly

### Post-Deployment

- [ ] Test end-to-end flow
- [ ] Verify WebSocket connections
- [ ] Test on mobile devices
- [ ] Check error logging
- [ ] Monitor resource usage
- [ ] Set up alerts (optional)

---

## Alternative Hosting Options

### Backend Alternatives

1. **Fly.io**
   - Global edge deployment
   - Similar to Railway
   - Free tier available

2. **DigitalOcean App Platform**
   - $5/month for basic app
   - Easy PostgreSQL integration

3. **AWS/GCP/Azure**
   - More complex setup
   - Higher cost
   - Better for large scale

### Frontend Alternatives

1. **Netlify**
   - Similar to Vercel
   - Free tier
   - Good Next.js support

2. **Cloudflare Pages**
   - Free tier
   - Global CDN
   - Next.js support improving

---

## Cost Optimization Tips

1. **Use smaller Whisper model:**
   - `tiny` model is 39MB vs `base` 74MB
   - Faster inference, lower memory

2. **Enable caching:**
   - Cache translations in Redis/memory
   - Reduce API calls to LibreTranslate

3. **Optimize database queries:**
   - Add indexes on frequently queried columns
   - Limit history results

4. **Use free tier limits wisely:**
   - Railway: $5 credit/month usually enough
   - Render: 750 hours/month = always-on for 1 service
   - Vercel: Unlimited for personal projects

---

## Support & Resources

- **Railway Docs:** https://docs.railway.app
- **Render Docs:** https://render.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/
- **Next.js Deployment:** https://nextjs.org/docs/deployment

---

## Summary

Deploying the Audio Auto-Translator:

1. **Backend** → Railway/Render (with PostgreSQL)
2. **Frontend** → Vercel (with env vars)
3. **Configure** → CORS, WebSocket URLs
4. **Test** → End-to-end flow
5. **Monitor** → Logs and metrics

**Estimated Time:** 30-60 minutes for first deployment

**Recommended Stack:**
- Frontend: **Vercel** (free, unlimited)
- Backend: **Railway** ($5/month, best DX)
- Database: **Railway PostgreSQL** (included)

**Total Cost:** ~$5/month (with Railway credit, often free)

Happy deploying! 🚀
