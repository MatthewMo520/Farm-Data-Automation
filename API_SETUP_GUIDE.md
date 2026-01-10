# API Setup Guide - Get Your Own API Keys

This guide shows you how to set up ALL the API keys and credentials you need from scratch. You don't need any existing credentials - we'll create everything together!

---

## Overview: What APIs Do You Need?

### Required (FREE)
1. **Groq AI** - FREE AI data extraction (14,400 requests/day free)
2. **Azure AD** - FREE app registration for Dynamics 365 access

### Optional (Paid - Only if you want faster transcription)
3. **OpenAI Whisper API** - Paid transcription (~$0.006/min) - Only if you don't want FREE local Whisper

**Total Cost: $0/month** (if you use FREE local Whisper + FREE Groq)

---

## 1. Groq AI Setup (FREE - REQUIRED)

Groq provides FREE AI-powered data extraction using Llama 3.1 70B model.

### Step 1: Create Groq Account

1. Go to: https://console.groq.com/
2. Click **"Sign Up"** or **"Get Started"**
3. Sign up with Google, GitHub, or email
4. Verify your email (check spam folder)
5. Login to the console

### Step 2: Generate API Key

1. Once logged in, click **"API Keys"** in the left sidebar
   - Or go directly to: https://console.groq.com/keys
2. Click **"Create API Key"**
3. Give it a name: `Farm Data Automation`
4. Click **"Submit"**
5. **COPY THE KEY IMMEDIATELY** - You can't see it again!
   - It looks like: `gsk_1234567890abcdefghijklmnopqrstuvwxyz`

### Step 3: Save to .env File

Add to your `.env` file:
```bash
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_TEMPERATURE=0.1
```

### Free Tier Limits
- **14,400 requests per day** (FREE)
- **30 requests per minute**
- More than enough for farm operations!

**Cost: $0/month** ✅

---

## 2. Azure AD Setup (FREE - REQUIRED FOR DYNAMICS)

Follow the **AZURE_SETUP_QUICK_GUIDE.md** file for detailed steps.

### Quick Summary:

1. Login to: https://portal.azure.com
2. Create App Registration
3. Get these 3 values:
   - Application (client) ID
   - Directory (tenant) ID
   - Client Secret
4. Grant Dynamics CRM permissions
5. Add app user to Dynamics 365

### Save to .env File

```bash
DYNAMICS_BASE_URL=https://agsights.crm3.dynamics.com
DYNAMICS_CLIENT_ID=your_application_client_id
DYNAMICS_CLIENT_SECRET=your_client_secret
DYNAMICS_TENANT_ID=your_tenant_id
```

**Cost: $0** (Azure AD app registration is free) ✅

---

## 3. OpenAI Whisper API (OPTIONAL - PAID)

**Note: You DON'T need this if you use FREE local Whisper!**

Only set this up if you want faster transcription (5-10 seconds vs 10-20 seconds).

### Step 1: Create OpenAI Account

1. Go to: https://platform.openai.com/signup
2. Sign up with email or Google
3. Verify your email
4. Login to dashboard

### Step 2: Add Payment Method

1. Click your profile icon (top right)
2. Click **"Billing"**
3. Click **"Payment methods"**
4. Add a credit/debit card
5. Add initial credit ($5-10 minimum)

### Step 3: Generate API Key

1. Click **"API keys"** in left sidebar
   - Or go to: https://platform.openai.com/api-keys
2. Click **"Create new secret key"**
3. Name it: `Farm Data Automation`
4. Click **"Create secret key"**
5. **COPY THE KEY IMMEDIATELY** - You can't see it again!
   - It looks like: `sk-proj-1234567890abcdefghijklmnopqrstuvwxyz`

### Step 4: Save to .env File

```bash
# Use OpenAI API for transcription
WHISPER_MODE=api
WHISPER_API_KEY=sk-proj-your_actual_key_here
WHISPER_MODEL=whisper-1
```

### Cost Estimate
- **~$0.006 per minute** of audio
- Example: 100 recordings/month × 2 min each = $1.20/month

**Recommendation: Use FREE local Whisper instead!**

---

## 4. Local Whisper Setup (FREE - RECOMMENDED)

This is 100% FREE and works offline! No API key needed.

### Installation

```bash
# Activate your virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install local Whisper (one-time)
pip install openai-whisper
```

### Configuration

Add to your `.env` file:
```bash
# Use FREE local Whisper
WHISPER_MODE=local
WHISPER_LOCAL_MODEL=base  # Recommended: good balance of speed and quality
```

**First run will download the model (142MB) - one-time download.**

### Model Options

| Model | Size | Speed | Quality | Recommendation |
|-------|------|-------|---------|----------------|
| tiny | 75MB | Very Fast (5-10s) | Basic | If speed is critical |
| **base** | **142MB** | **Fast (10-20s)** | **Good** | **RECOMMENDED** |
| small | 466MB | Medium (20-40s) | Better | If quality is priority |
| medium | 1.5GB | Slow (40-60s) | Excellent | Overkill for farm use |
| large | 2.9GB | Very Slow (60-120s) | Best | Not needed |

**Cost: $0/month** ✅

See **FREE_WHISPER_SETUP.md** for more details.

---

## 5. Database Setup (FREE)

### Local Development (SQLite)

No setup needed! SQLite is built into Python.

Your `.env` file:
```bash
# SQLite (default - no configuration needed)
# DATABASE_URL will auto-default to sqlite+aiosqlite:///./farm_data.db
```

**Cost: $0** ✅

### Production (PostgreSQL - FREE Options)

**Railway.app (FREE Tier):**
1. Create Railway account: https://railway.app/
2. Create new project
3. Add PostgreSQL database
4. Copy the DATABASE_URL they provide
5. Add to your `.env`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ```

**Render.com (FREE Tier):**
1. Create Render account: https://render.com/
2. Create PostgreSQL database
3. Copy the Internal Database URL
4. Add to your `.env`:
   ```bash
   DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
   ```

**Cost: $0** (Free tier) ✅

---

## 6. Storage Setup (FREE)

### Local Storage (Recommended for MVP)

No API needed! Files are stored on your server.

Your `.env` file:
```bash
# Auto-detects environment
# Development: ./storage/recordings
# Production: /app/storage/recordings
# LOCAL_STORAGE_PATH=/custom/path  # Only if you need custom path
```

**Cost: $0** ✅

### Azure Blob Storage (OPTIONAL - If you need cloud storage)

1. Go to: https://portal.azure.com
2. Create Storage Account
3. Get connection string
4. Add to `.env`:
   ```bash
   AZURE_STORAGE_CONNECTION_STRING=your_connection_string
   AZURE_STORAGE_CONTAINER_NAME=voice-recordings
   ```

**Cost: ~$0.01-0.05/month** for typical farm usage

**Recommendation: Use local storage for MVP!**

---

## 7. Security Settings (REQUIRED)

### Generate Secret Key

Run this command to generate a secure random key:

**Windows (PowerShell):**
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Mac/Linux:**
```bash
openssl rand -hex 32
```

This will output something like:
```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Save to .env File

```bash
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**CRITICAL: Never share this key! Generate a new one for each environment.**

---

## Complete .env File Template

Here's what your `.env` file should look like:

```bash
# ========================================
# ENVIRONMENT
# ========================================
ENVIRONMENT=production  # or "development" for local
APP_NAME=Farm Data Automation
DEBUG=False
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com

# ========================================
# DATABASE
# ========================================
# SQLite (local development - auto-default, no need to set)
# DATABASE_URL=sqlite+aiosqlite:///./farm_data.db

# PostgreSQL (production - get from Railway/Render)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# ========================================
# WHISPER TRANSCRIPTION (Choose one)
# ========================================
# Option 1: FREE Local Whisper (RECOMMENDED)
WHISPER_MODE=local
WHISPER_LOCAL_MODEL=base

# Option 2: OpenAI Whisper API (Paid, faster)
# WHISPER_MODE=api
# WHISPER_API_KEY=sk-proj-your_openai_key_here
# WHISPER_MODEL=whisper-1

# ========================================
# GROQ AI (REQUIRED - FREE)
# ========================================
GROQ_API_KEY=gsk_your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_TEMPERATURE=0.1

# ========================================
# DYNAMICS 365 (REQUIRED)
# ========================================
DYNAMICS_BASE_URL=https://agsights.crm3.dynamics.com
DYNAMICS_CLIENT_ID=your_azure_ad_app_client_id
DYNAMICS_CLIENT_SECRET=your_azure_ad_app_client_secret
DYNAMICS_TENANT_ID=your_azure_ad_tenant_id

# ========================================
# STORAGE (Local by default)
# ========================================
# Auto-detects: ./storage/recordings (dev) or /app/storage/recordings (prod)
# LOCAL_STORAGE_PATH=/custom/path  # Only if needed

# ========================================
# SECURITY (REQUIRED)
# ========================================
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Cost Summary

### FREE Configuration (Recommended)
- Transcription: **$0** (Local Whisper)
- AI Extraction: **$0** (Groq free tier)
- Database: **$0** (SQLite or PostgreSQL free tier)
- Storage: **$0** (Local files)
- Azure AD: **$0** (Free)
- **Total: $0/month** 🎉

### With OpenAI Whisper API
- Transcription: **~$1-6/month** (OpenAI API)
- Everything else: **$0**
- **Total: ~$1-6/month**

---

## Setup Order

Follow this order to set everything up:

1. ✅ **Groq AI** (5 minutes) - Get API key
2. ✅ **Local Whisper** (5 minutes) - Install package
3. ✅ **Secret Key** (1 minute) - Generate security key
4. ✅ **Azure AD** (20 minutes) - Follow AZURE_SETUP_QUICK_GUIDE.md
5. ✅ **Database** (optional - if deploying) - Set up PostgreSQL
6. ✅ **Create .env file** - Copy template and fill in your values

**Total Time: 30-45 minutes**

---

## Testing Your Setup

After setting up all APIs, test each one:

### Test 1: Server Starts
```bash
python -m backend.main
```
Should see: `Uvicorn running on http://0.0.0.0:8000`

### Test 2: Login Works
1. Go to http://localhost:8000
2. Login with default credentials
3. Should see dashboard

### Test 3: Groq AI Works
Upload a test recording - should extract data successfully

### Test 4: Whisper Works
Check transcription in logs - should see transcription text

### Test 5: Dynamics Sync Works
After Azure setup - verify animal created in Dynamics 365

---

## Troubleshooting

### Error: "Invalid Groq API Key"
- Double-check you copied the full key (starts with `gsk_`)
- Make sure no spaces before/after the key
- Generate a new key if needed

### Error: "Whisper model not found"
- Run: `pip install openai-whisper`
- First run downloads model automatically (needs internet)

### Error: "Database connection failed"
- Check DATABASE_URL format
- Verify credentials are correct
- For PostgreSQL, ensure database exists

### Error: "Dynamics authentication failed"
- Verify all 3 Azure AD credentials
- Check if app user added to Dynamics 365
- Verify permissions granted

---

## Security Best Practices

1. **Never commit .env file** - Already in .gitignore ✅
2. **Use different keys** for dev/staging/production
3. **Rotate secrets** every 6-12 months
4. **Limit API key** permissions to only what's needed
5. **Monitor API usage** to detect unauthorized access

---

## Need Help?

- **Groq Issues:** https://console.groq.com/docs
- **OpenAI Issues:** https://platform.openai.com/docs
- **Azure Issues:** See AZURE_SETUP_QUICK_GUIDE.md
- **Whisper Issues:** See FREE_WHISPER_SETUP.md

---

**You're now ready to set up all APIs from scratch!** 🚀
