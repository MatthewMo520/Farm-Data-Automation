# Testing Guide - Verify Everything Works (Without Dynamics)

This guide shows you how to test the entire system EXCEPT the Dynamics 365 sync. Perfect for verifying everything before you get your Azure credentials!

---

## What You'll Test

1. ✅ Server starts correctly
2. ✅ Dashboard login works
3. ✅ Audio upload works
4. ✅ FREE Whisper transcription works (speech-to-text)
5. ✅ FREE Groq AI extraction works
6. ✅ Database storage works
7. ⏳ Dynamics sync (will fail gracefully without credentials)

**Time Required: 5-10 minutes**

---

## Step 1: Start the Server (If Not Running)

```bash
# Navigate to project folder
cd C:\Farm-Data-Automation  # Windows
cd ~/Farm-Data-Automation   # Mac/Linux

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Start server
python -m backend.main
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [...]
2026-01-10 XX:XX:XX - backend.main - INFO - Starting up Farm Data Automation API...
2026-01-10 XX:XX:XX - backend.main - INFO - Database initialized
INFO:     Application startup complete.
```

✅ **If you see this, server is running!**

**Keep this terminal window open** - you'll watch the logs here!

---

## Step 2: Access the Dashboard

1. Open web browser
2. Go to: **http://localhost:8000**
3. You should see the login page with:
   - 🌾 Farm Data Automation header
   - Login form
   - Green agricultural color scheme

✅ **If you see the login page, frontend is working!**

---

## Step 3: Login

**Use default credentials:**
- Username: `demo@biotrack.ca`
- Password: `bioTrack+test`

Click **"Sign In"**

**Expected Result:**
- Redirects to dashboard
- Shows "Welcome, bioTrack+ Demo" (or similar)
- Shows empty recordings list
- Shows recording interface (microphone or upload)

✅ **If you see the dashboard, authentication works!**

---

## Step 4: Create a Test Recording

You have 2 options:

### Option A: Upload an Audio File

1. Click **"Choose File"** button
2. Select any audio file (MP3, WAV, M4A, WebM)
3. Don't have one? Record one on your phone saying:
   > "Add a new heifer, ear tag 1234, born on January 1st, 2025"

### Option B: Record in Browser (If Supported)

1. Click the **microphone icon** (if available)
2. Allow microphone access when prompted
3. Say something like:
   > "Add a new animal, ear tag 5678, born January 5th, 2025, it's a bull calf"
4. Click stop recording

---

## Step 5: Submit and Watch Processing

1. Click **"Submit Recording"** button
2. Watch the status in the dashboard

**You should see status change:**
```
UPLOADED → TRANSCRIBING → PROCESSING → ERROR (or COMPLETED)
```

**This is normal!** It will fail at the Dynamics sync step because we don't have Azure credentials yet.

---

## Step 6: Check the Server Logs

**Switch to your terminal window where the server is running.**

You should see detailed logs like this:

### ✅ UPLOAD SUCCESS:
```
INFO:     127.0.0.1:XXXXX - "POST /api/v1/recordings/ HTTP/1.1" 200 OK
File uploaded successfully: [some-id]/[date]/[filename]
```

### ✅ TRANSCRIPTION SUCCESS (This is the important one!):
```
[recording-id] Using FREE local Whisper (model: base)
[recording-id] Starting transcription...
[recording-id] Transcription successful
[recording-id] Transcription text: "Add a new heifer, ear tag 1234, born on January 1st, 2025"
[recording-id] Confidence: HIGH
```

**If you see this, Whisper transcription is WORKING!** 🎉

### ✅ AI EXTRACTION SUCCESS:
```
[recording-id] Extracting structured data with Groq AI...
[recording-id] Successfully extracted data
[recording-id] Extracted data: {"ear_tag": "1234", "birth_date": "2025-01-01", "category": "heifer", ...}
[recording-id] Confidence: HIGH
```

**If you see this, Groq AI extraction is WORKING!** 🎉

### ⚠️ DYNAMICS SYNC FAILURE (Expected!):
```
[recording-id] Syncing to Dynamics 365...
ERROR - [recording-id] Dynamics sync failed: Invalid Azure AD credentials
[recording-id] Status: ERROR
```

**This is EXPECTED** because you haven't set up Azure credentials yet!

---

## Step 7: View Recording Details in Dashboard

1. Go back to the browser dashboard
2. Click **"View Details"** on your recording
3. You should see:

**✅ What Should Be There:**
- **Status:** ERROR (or COMPLETED if you have Dynamics set up)
- **Transcription Text:** Your full spoken text
- **Extracted Data:**
  - Ear Tag: 1234
  - Birth Date: 2025-01-01
  - Category: heifer
  - (and other fields)
- **Confidence Score:** HIGH or MEDIUM
- **Error Message:** "Dynamics sync failed..." (if no Azure credentials)

**✅ This proves:**
1. Upload works ✅
2. Transcription works ✅
3. AI extraction works ✅
4. Database storage works ✅
5. Only Dynamics sync is waiting for Azure credentials ⏳

---

## Step 8: Check Database Directly (Optional)

Want to see the data in the database?

```bash
# Open SQLite database
sqlite3 farm_data.db

# View all recordings
SELECT id, filename, status, transcription_text, extracted_data FROM recordings;

# Exit
.quit
```

You should see your recording with all the transcribed text and extracted data stored!

---

## What Each Status Means

| Status | Meaning | What's Happening |
|--------|---------|------------------|
| **UPLOADED** | File received | Audio saved to storage |
| **TRANSCRIBING** | Converting speech to text | Whisper is processing |
| **PROCESSING** | Extracting data | Groq AI is analyzing |
| **SYNCING** | Sending to Dynamics | Calling Dynamics 365 API |
| **SYNCED** | ✅ Complete! | Animal created in bioTrack+ |
| **ERROR** | ❌ Failed | Check logs for details |

---

## Verification Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000
- [ ] Can login with demo credentials
- [ ] Can upload or record audio
- [ ] Status changes from UPLOADED → TRANSCRIBING
- [ ] Server logs show "Transcription successful"
- [ ] Server logs show transcribed text (your spoken words)
- [ ] Status changes to PROCESSING
- [ ] Server logs show "Successfully extracted data"
- [ ] Server logs show extracted fields (ear_tag, birth_date, etc.)
- [ ] Status changes to ERROR (expected without Azure credentials)
- [ ] Can view recording details in dashboard
- [ ] Can see transcription text in dashboard
- [ ] Can see extracted data in dashboard

**If all checked except the last ERROR → Everything works!** 🎉

The only missing piece is Azure AD credentials for Dynamics sync.

---

## Common Issues and Solutions

### Issue: "No module named 'whisper'"

**Cause:** Whisper package not installed

**Solution:**
```bash
pip install openai-whisper
```

### Issue: Transcription status stuck

**Cause:** Whisper model downloading (first time only)

**Solution:** Wait 2-5 minutes - it's downloading the 142MB model. You'll see in logs:
```
Downloading whisper model...
```

### Issue: "Invalid Groq API Key"

**Cause:** Groq API key not set or incorrect in .env

**Solution:**
1. Check `.env` file has: `GROQ_API_KEY=gsk_...`
2. Verify no spaces before/after the key
3. Get new key at https://console.groq.com/keys
4. Restart server after updating .env

### Issue: Status goes directly to ERROR

**Cause:** Check server logs for specific error

**Common reasons:**
- Groq API key missing or invalid
- Whisper package not installed
- File format not supported

**Solution:** Read the error message in server logs and fix accordingly

### Issue: Can't hear transcription output

**Clarification:** This is **speech-to-text** (voice → text), not text-to-speech (text → voice). You won't hear anything - you'll **see** the transcribed text in the dashboard and logs!

---

## Example: Perfect Test Run

Here's what a successful test looks like:

### 1. Upload Audio
You upload a file saying: *"Add a new bull, ear tag 9999, born March 15th, 2024"*

### 2. Server Logs Show:
```
✅ File uploaded successfully
✅ Using FREE local Whisper (model: base)
✅ Transcription successful
✅ Transcription text: "Add a new bull, ear tag 9999, born March 15th, 2024"
✅ Successfully extracted data
✅ Extracted: {"ear_tag": "9999", "birth_date": "2024-03-15", "category": "bull"}
❌ Dynamics sync failed: Invalid credentials
```

### 3. Dashboard Shows:
- **Status:** ERROR
- **Transcription:** "Add a new bull, ear tag 9999, born March 15th, 2024"
- **Extracted Data:**
  - Ear Tag: 9999
  - Birth Date: 2024-03-15
  - Category: bull
- **Error:** Dynamics authentication failed

**This is PERFECT!** Everything works except Dynamics (which needs Azure credentials).

---

## What To Do After Successful Test

### If Everything Works (Except Dynamics Sync):

1. ✅ **You're ready for Azure setup!**
2. Follow **AZURE_SETUP_QUICK_GUIDE.md** to get your 3 credentials
3. Run the credentials update script
4. Test again - this time it should go to SYNCED status!
5. Check Dynamics 365 to see the animal record

### If Something Doesn't Work:

1. Check server logs for specific error
2. Review this guide's "Common Issues" section
3. Verify .env file has all required values
4. Check FIRST_TIME_SETUP.md for installation steps
5. Review API_SETUP_GUIDE.md for API key setup

---

## Quick Test Script

Want to test quickly without manual upload? Run this:

```bash
# Create a test audio file (text-to-speech)
# Mac:
say "Add a new heifer, ear tag 1234, born January first, 2025" -o test.aiff

# Windows (using PowerShell):
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.SetOutputToWaveFile("test.wav")
$speak.Speak("Add a new heifer, ear tag 1234, born January first, 2025")
$speak.Dispose()

# Linux (install espeak first: sudo apt install espeak):
espeak "Add a new heifer, ear tag 1234, born January first, 2025" -w test.wav
```

Then upload test.wav/test.aiff through the dashboard!

---

## Next Steps

### After Verifying Everything Works:

1. **Get Azure Credentials**
   - Follow AZURE_SETUP_QUICK_GUIDE.md
   - 15-30 minutes
   - Completely FREE

2. **Update Database**
   ```bash
   python scripts/quick_update_creds.py "CLIENT_ID" "TENANT_ID" "SECRET"
   ```

3. **Test Again**
   - Upload same test recording
   - Should now go to SYNCED status
   - Check Dynamics 365 for the animal record

4. **Ready for Production!**
   - See COMPLETE_HOSTING_GUIDE.md for deployment
   - See CLIENT_HANDOVER.md for user guide

---

## Summary

**What Works Without Azure:**
- ✅ Server startup
- ✅ Dashboard and login
- ✅ File upload/recording
- ✅ FREE Whisper transcription
- ✅ FREE Groq AI extraction
- ✅ Database storage
- ✅ Data visualization

**What Needs Azure:**
- ⏳ Dynamics 365 sync (creating animal records)

**Cost So Far:** $0

**Next Step:** Get Azure credentials to complete the pipeline!

---

**Happy Testing!** 🧪

If everything above works, you have a fully functional $0/month AI-powered voice transcription and data extraction system! The only missing piece is the Dynamics sync. 🎉
