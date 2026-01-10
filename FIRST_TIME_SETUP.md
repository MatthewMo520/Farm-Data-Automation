# First-Time Setup Guide - From Zero to Running Application

This is your **starting point**! Follow this guide to go from downloading the code to having a fully working farm automation system.

**Time Required: 1-2 hours (mostly waiting for downloads)**

---

## Overview: What You're Setting Up

By the end of this guide, you'll have:
- ✅ Voice recording system running
- ✅ FREE AI-powered transcription
- ✅ FREE data extraction
- ✅ Connection to your Dynamics 365 (bioTrack+)
- ✅ Web dashboard to manage recordings

**Total Cost: $0/month** (using FREE services)

---

## Prerequisites

Before starting, make sure you have:
- [ ] Computer (Windows, Mac, or Linux)
- [ ] Internet connection
- [ ] Admin access to your Dynamics 365 account (for Azure setup)
- [ ] 30 GB free disk space (for Python, dependencies, and Whisper model)
- [ ] Basic computer skills (can download files, edit text files)

---

## Step 1: Install Python (15 minutes)

### Windows

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.11** or newer
3. Run the installer
4. ✅ **IMPORTANT: Check "Add Python to PATH"**
5. Click "Install Now"
6. Wait for installation to complete

**Test it worked:**
```bash
# Open Command Prompt (press Win + R, type cmd, press Enter)
python --version
```
Should show: `Python 3.11.x` or higher

### Mac

1. Open Terminal
2. Install Homebrew (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Install Python:
   ```bash
   brew install python@3.11
   ```

**Test it worked:**
```bash
python3 --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git -y
```

**Test it worked:**
```bash
python3 --version
```

---

## Step 2: Download the Code (5 minutes)

### Option A: Download ZIP (Easiest)

1. Go to your GitHub repository (where you host this code)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file to a folder, e.g.:
   - Windows: `C:\Farm-Data-Automation`
   - Mac: `~/Farm-Data-Automation`
   - Linux: `~/Farm-Data-Automation`

### Option B: Clone with Git

```bash
# Navigate to where you want the project
cd C:\Projects  # Windows
cd ~/Projects   # Mac/Linux

# Clone repository
git clone https://github.com/yourusername/Farm-Data-Automation.git
cd Farm-Data-Automation
```

---

## Step 3: Create Virtual Environment (5 minutes)

A virtual environment keeps all Python packages isolated for this project.

```bash
# Navigate to project folder
cd C:\Farm-Data-Automation  # Windows
cd ~/Farm-Data-Automation   # Mac/Linux

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

You should see `(venv)` before your command prompt.

---

## Step 4: Install Dependencies (5-10 minutes)

This installs all the Python packages the system needs.

```bash
# Make sure virtual environment is activated (you see (venv) in prompt)
pip install -r requirements.txt
```

**This will:**
- Download ~2GB of packages
- Install FastAPI, SQLAlchemy, Whisper, Groq, etc.
- Take 5-10 minutes depending on internet speed

**If you see errors about Microsoft C++ Build Tools (Windows):**
1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"
3. Restart and try `pip install -r requirements.txt` again

---

## Step 5: Get API Keys (20-30 minutes)

You need API keys to use the AI services. Follow **API_SETUP_GUIDE.md** for detailed steps.

### Quick Summary:

#### 5.1: Groq AI (FREE - REQUIRED)

1. Go to: https://console.groq.com/
2. Sign up (free)
3. Click "API Keys" → "Create API Key"
4. Name it: `Farm Automation`
5. Copy the key (starts with `gsk_`)
6. **Save it in Notepad** - you'll need it soon!

#### 5.2: Azure AD (FREE - REQUIRED)

1. Follow **AZURE_SETUP_QUICK_GUIDE.md**
2. Get 3 credentials:
   - Application (client) ID
   - Directory (tenant) ID
   - Client Secret
3. **Save all 3 in Notepad**

**This is the longest step - take your time!**

---

## Step 6: Create .env File (5 minutes)

This file stores all your API keys and configuration.

### Copy the template:

```bash
# Windows Command Prompt
copy .env.example .env

# Mac/Linux Terminal
cp .env.example .env
```

### Edit .env file:

Open `.env` file in a text editor (Notepad, VS Code, etc.) and fill in:

```bash
# ========================================
# ENVIRONMENT
# ========================================
ENVIRONMENT=production
APP_NAME=Farm Data Automation
DEBUG=False

# ========================================
# DATABASE (Use SQLite for local - no changes needed)
# ========================================
# DATABASE_URL will auto-default to SQLite

# ========================================
# WHISPER TRANSCRIPTION (FREE Local)
# ========================================
WHISPER_MODE=local
WHISPER_LOCAL_MODEL=base

# ========================================
# GROQ AI (Paste your Groq API key here)
# ========================================
GROQ_API_KEY=gsk_YOUR_GROQ_KEY_HERE  # Replace with your actual key
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_TEMPERATURE=0.1

# ========================================
# DYNAMICS 365 (Paste your Azure AD credentials)
# ========================================
DYNAMICS_BASE_URL=https://agsights.crm3.dynamics.com
DYNAMICS_CLIENT_ID=YOUR_APPLICATION_CLIENT_ID_HERE  # From Azure
DYNAMICS_CLIENT_SECRET=YOUR_CLIENT_SECRET_HERE      # From Azure
DYNAMICS_TENANT_ID=YOUR_TENANT_ID_HERE              # From Azure

# ========================================
# SECURITY (Generate a secret key)
# ========================================
SECRET_KEY=REPLACE_THIS_WITH_RANDOM_STRING  # See below
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Generate SECRET_KEY:

Run this command to generate a secure random key:

```bash
# Windows/Mac/Linux (in your activated venv)
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as your `SECRET_KEY` value.

**Save the file!**

---

## Step 7: Initialize Database (2 minutes)

Create the demo client with login credentials:

```bash
# Make sure you're in project folder with venv activated
python scripts/seed_demo_client.py
```

You should see:
```
[OK] Created demo client: bioTrack+ Demo
[OK] Created bioTrack animal schema mapping
```

---

## Step 8: Update Azure Credentials in Database (2 minutes)

Now add your Azure AD credentials to the database:

```bash
python scripts/quick_update_creds.py "YOUR_CLIENT_ID" "YOUR_TENANT_ID" "YOUR_CLIENT_SECRET"
```

Replace with your actual values from Step 5.2.

**Example:**
```bash
python scripts/quick_update_creds.py "a1b2c3d4-e5f6-7890-abcd-ef1234567890" "f9e8d7c6-b5a4-3210-fedc-ba0987654321" "abc123~XYZ789.secretvalue"
```

You should see:
```
======================================================================
SUCCESS: Dynamics 365 credentials updated!
======================================================================
```

---

## Step 9: Start the Server (1 minute)

```bash
# Make sure venv is activated
python -m backend.main
```

You should see:
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [...]
INFO:     Application startup complete.
```

**Leave this terminal window open!**

---

## Step 10: Access the Dashboard (1 minute)

1. Open your web browser
2. Go to: **http://localhost:8000**
3. You should see the login page

**Default Login Credentials:**
- Username: `demo@biotrack.ca`
- Password: `bioTrack+test`

4. Click **"Sign In"**
5. You should see the dashboard!

---

## Step 11: Test the System (5 minutes)

### Test 1: Upload a Recording

1. Click **"Choose File"** or use the microphone icon
2. Select or record an audio file saying something like:
   ```
   "Add a new animal. Ear tag 1234. Born on January 1st, 2025. It's a heifer."
   ```
3. Click **"Submit Recording"**
4. Watch the status change:
   - UPLOADED → TRANSCRIBING → PROCESSING → SYNCED ✅

### Test 2: Check Transcription

1. Wait for status to show "SYNCED" (30-60 seconds)
2. Click **"View Details"** on the recording
3. You should see:
   - ✅ Transcription text
   - ✅ Extracted data (ear tag, birth date, category)
   - ✅ Confidence score

### Test 3: Verify in Dynamics 365

1. Open https://agsights.crm3.dynamics.com
2. Go to Animals list
3. Look for the newly created animal record
4. Verify all fields match what you said in the recording

**If all 3 tests pass - CONGRATULATIONS! Your system is fully working!** 🎉

---

## Common Issues and Solutions

### Issue: "Python not found"
**Solution:** Restart your terminal/command prompt after installing Python

### Issue: "pip: command not found"
**Solution:** Use `python -m pip` instead of `pip`

### Issue: "Permission denied" (Mac/Linux)
**Solution:** Use `sudo` before commands, e.g., `sudo python -m pip install ...`

### Issue: "ModuleNotFoundError: No module named 'whisper'"
**Solution:**
```bash
pip install openai-whisper
```

### Issue: "Database locked"
**Solution:** Close any other programs that might be accessing the database

### Issue: "Invalid Groq API Key"
**Solution:**
- Check you copied the full key (starts with `gsk_`)
- Make sure no spaces before/after in .env file
- Generate a new key at https://console.groq.com/keys

### Issue: "Dynamics authentication failed"
**Solution:**
- Verify all 3 Azure credentials are correct
- Check that app user was added to Dynamics 365
- Verify API permissions were granted

### Issue: Server starts but can't access http://localhost:8000
**Solution:**
- Check firewall isn't blocking port 8000
- Try http://127.0.0.1:8000 instead
- Check server logs for errors

---

## What's Next?

Now that your system is running, you can:

### 1. Deploy to Production
- See **COMPLETE_HOSTING_GUIDE.md** for deployment options
- Start with local server or Railway.app (FREE)

### 2. Customize for Your Farm
- Add more users (edit database or create admin interface)
- Customize animal fields (edit schema mapping)
- Add more entity types (sheep, goats, etc.)

### 3. Train Users
- Show farmers how to record voice notes
- Create quick reference guide
- Set up support process

### 4. Monitor and Optimize
- Check logs regularly
- Monitor API usage (Groq dashboard)
- Collect user feedback
- Adjust AI prompts if needed

---

## Important Files Reference

- **API_SETUP_GUIDE.md** - How to get all API keys
- **AZURE_SETUP_QUICK_GUIDE.md** - Detailed Azure AD setup
- **COMPLETE_HOSTING_GUIDE.md** - Deployment options
- **CLIENT_HANDOVER.md** - Complete user guide
- **FREE_WHISPER_SETUP.md** - Free transcription details
- **PRODUCTION_READINESS.md** - Technical documentation

---

## Need Help?

### Documentation
Read the guides in this order:
1. FIRST_TIME_SETUP.md (this file)
2. API_SETUP_GUIDE.md
3. COMPLETE_HOSTING_GUIDE.md
4. CLIENT_HANDOVER.md

### Troubleshooting
- Check logs in terminal where server is running
- Review PRODUCTION_READINESS.md (Known Issues section)
- Check .env file for typos

### Resources
- FastAPI: https://fastapi.tiangolo.com/
- Whisper: https://github.com/openai/whisper
- Groq: https://console.groq.com/docs

---

## Checklist Summary

- [ ] Python 3.11+ installed
- [ ] Code downloaded/cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Groq API key obtained
- [ ] Azure AD credentials obtained (3 values)
- [ ] .env file created and filled in
- [ ] SECRET_KEY generated
- [ ] Database initialized (`seed_demo_client.py`)
- [ ] Azure credentials added to database
- [ ] Server started successfully
- [ ] Can access dashboard at http://localhost:8000
- [ ] Can login with demo credentials
- [ ] Test recording processed successfully
- [ ] Verified record created in Dynamics 365

**If all checked - you're ready to go!** 🚀

---

**Estimated Total Time:** 1-2 hours

**Total Cost:** $0/month (using FREE tier services)

**You now have a fully functional farm data automation system!**
