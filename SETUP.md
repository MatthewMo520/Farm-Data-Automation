# Setup Guide - Get Started in 1 Hour

Complete setup guide from downloading the code to having a fully working voice automation system.

**Total Time: 1-2 hours**
**Total Cost: $0/month**

---

## What You're Building

A voice-to-database automation system:
- Farmers speak → System transcribes → AI extracts data → Creates records in Dynamics 365
- **100% FREE** operational cost (using free AI services)

---

## Prerequisites

- Computer (Windows, Mac, or Linux)
- Internet connection
- Python 3.11+ (we'll install this)
- Admin access to your Dynamics 365 account
- 30GB free disk space

---

## Step 1: Install Python (15 minutes)

### Windows

1. Download Python: https://www.python.org/downloads/
2. Download **Python 3.11** or newer
3. Run installer
4. ✅ **CRITICAL: Check "Add Python to PATH"**
5. Click "Install Now"

**Test it:**
```bash
python --version
```
Should show: Python 3.11.x or higher

### Mac

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git -y
python3 --version
```

---

## Step 2: Download the Code (5 minutes)

### Option A: Download ZIP

1. Go to the GitHub repository
2. Click green "Code" button → "Download ZIP"
3. Extract to a folder:
   - Windows: `C:\Farm-Automation`
   - Mac/Linux: `~/Farm-Automation`

### Option B: Clone with Git

```bash
git clone <repository-url>
cd Farm-Automation
```

---

## Step 3: Install Dependencies (10 minutes)

```bash
# Navigate to project folder
cd Farm-Automation  # or wherever you extracted it

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install all packages (takes 5-10 minutes)
pip install -r requirements.txt
```

You should see packages installing. This downloads ~2GB of AI libraries.

---

## Step 4: Get API Keys (30 minutes)

You need 2 API keys (both FREE):

### 4A: Groq AI (5 minutes - FREE)

1. Go to: https://console.groq.com/
2. Sign up (free account)
3. Click "API Keys" → "Create API Key"
4. Name: `Farm Automation`
5. **Copy the key** (starts with `gsk_`)
6. Save in Notepad - you need this next!

### 4B: Azure AD for Dynamics 365 (25 minutes - FREE)

**You'll need your Dynamics 365 admin to help with this.**

Follow these steps in Azure Portal:

1. **Login to Azure Portal**: https://portal.azure.com
2. **Create App Registration**:
   - Search for "App registrations"
   - Click "+ New registration"
   - Name: `Farm Voice Automation`
   - Account types: "Single tenant" (first option)
   - Click "Register"

3. **Get Credential #1 & #2**:
   - You'll see the app overview page
   - **Copy Application (client) ID** → Save in Notepad
   - **Copy Directory (tenant) ID** → Save in Notepad

4. **Create Client Secret (Credential #3)**:
   - Left sidebar → "Certificates & secrets"
   - Click "+ New client secret"
   - Description: `Farm Automation Secret`
   - Expires: 24 months
   - Click "Add"
   - **⚠️ IMMEDIATELY copy the Value** → Save in Notepad
   - You can't see it again!

5. **Grant Dynamics Permissions**:
   - Left sidebar → "API permissions"
   - Click "+ Add a permission"
   - Scroll down → Click "Dynamics CRM"
   - Select "Delegated permissions"
   - Check "user_impersonation"
   - Click "Add permissions"
   - Click "Grant admin consent for [Your Org]"
   - Click "Yes"

6. **Add App User to Dynamics 365**:
   - Open your Dynamics 365: https://yourorg.crm3.dynamics.com
   - Click gear icon (⚙️) → "Advanced Settings"
   - Settings → Security → Users
   - Change view to "Application Users"
   - Click "+ New"
   - Change form to "Application User"
   - Paste Application ID from step 3
   - Press Tab (auto-fills fields)
   - Full Name: `Farm Voice Automation API`
   - Click "Save"
   - Click "Manage Roles"
   - Check "System Administrator" (or custom role with animal permissions)
   - Click "OK" → "Save & Close"

**You now have 3 credentials! Keep them safe.**

---

## Step 5: Configure Environment (5 minutes)

```bash
# Copy the template
cp .env.example .env  # Mac/Linux
copy .env.example .env  # Windows
```

Open `.env` in a text editor and fill in:

```bash
# Environment
ENVIRONMENT=production

# Groq AI (paste your key from step 4A)
GROQ_API_KEY=gsk_YOUR_GROQ_KEY_HERE
GROQ_MODEL=llama-3.1-70b-versatile

# Azure AD Dynamics (paste your 3 values from step 4B)
DYNAMICS_BASE_URL=https://yourorg.crm3.dynamics.com
DYNAMICS_CLIENT_ID=YOUR_APPLICATION_CLIENT_ID
DYNAMICS_CLIENT_SECRET=YOUR_CLIENT_SECRET_VALUE
DYNAMICS_TENANT_ID=YOUR_TENANT_ID

# Whisper (FREE local transcription)
WHISPER_MODE=local
WHISPER_LOCAL_MODEL=base

# Security (generate a random key)
SECRET_KEY=REPLACE_WITH_RANDOM_KEY
```

### Generate SECRET_KEY:

Run this command:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste as your SECRET_KEY.

**Save the file!**

---

## Step 6: Initialize Database (2 minutes)

```bash
# Make sure venv is activated
python scripts/seed_demo_client.py
```

You should see:
```
[OK] Created demo client
[OK] Created schema mapping
```

---

## Step 7: Update Azure Credentials (2 minutes)

```bash
python scripts/quick_update_creds.py "YOUR_CLIENT_ID" "YOUR_TENANT_ID" "YOUR_SECRET"
```

Replace with your actual values from step 4B.

You should see:
```
SUCCESS: Dynamics 365 credentials updated!
```

---

## Step 8: Start the Server (1 minute)

```bash
python -m backend.main
```

You should see:
```
INFO: Uvicorn running on http://0.0.0.0:8000
INFO: Application startup complete
```

**Keep this terminal open!**

---

## Step 9: Access the Dashboard

1. Open browser: **http://localhost:8000**
2. You should see the login page
3. Default credentials:
   - Username: `demo@example.com`
   - Password: `demo123`
4. Click "Sign In"

**You should see the dashboard!** 🎉

---

## Step 10: Test It!

1. Click the microphone icon or "Choose File"
2. Record or upload audio saying:
   > "Add a new heifer, ear tag 1234, born January 1st, 2025"
3. Click "Submit Recording"
4. Watch the status change:
   - UPLOADED → TRANSCRIBING → PROCESSING → SYNCED ✅

5. Check your Dynamics 365 to see the animal record!

**If you see SYNCED status - everything works!** 🎉

---

## Troubleshooting

### Server won't start

**Check Python version:**
```bash
python --version  # Need 3.11+
```

**Verify venv is activated:**
```bash
# You should see (venv) in your prompt
```

**Check .env file exists and has all values**

### "Invalid Groq API Key"

- Check key starts with `gsk_`
- No spaces before/after in .env
- Generate new key at https://console.groq.com/keys

### "Dynamics authentication failed"

- Verify all 3 Azure credentials are correct
- Check app user added to Dynamics 365
- Verify permissions granted

### Transcription fails

**First time:**
- Whisper downloads 142MB model (wait 2-5 minutes)
- Need internet for initial download

**Still failing:**
```bash
pip install openai-whisper
```

### Can't login

**Default credentials:**
- Username: `demo@example.com`
- Password: `demo123`

**Still can't login?** Check database was seeded:
```bash
python scripts/seed_demo_client.py
```

---

## What's Next?

### Deploy to Production

See **COMPLETE_HOSTING_GUIDE.md** for deployment options:
- Local Server (FREE)
- Railway.app (FREE tier)
- Render.com (FREE tier)
- DigitalOcean ($6/month)

### Customize

- Add more users
- Customize animal fields
- Add more entity types (sheep, goats, etc.)

---

## Cost Summary

**With This Setup:**
- Transcription: $0 (local Whisper)
- AI Extraction: $0 (Groq free tier)
- Storage: $0 (local files)
- Database: $0 (SQLite)
- Azure AD: $0 (free)

**Total: $0/month** ✅

Only ongoing cost is your existing Dynamics 365 license.

---

## Support

**Documentation:**
- **API_SETUP_GUIDE.md** - Detailed API key setup
- **COMPLETE_HOSTING_GUIDE.md** - All deployment options
- **FREE_WHISPER_SETUP.md** - Transcription details
- **TESTING_GUIDE.md** - Testing without Dynamics
- **PRODUCTION_READINESS.md** - Technical documentation

**Resources:**
- FastAPI: https://fastapi.tiangolo.com/
- Whisper: https://github.com/openai/whisper
- Groq: https://console.groq.com/docs

---

**Total Setup Time: 1-2 hours**
**You now have a $0/month voice automation system!** 🎉
