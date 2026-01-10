# Azure AD Setup Guide

Complete guide to set up Azure AD App Registration for Dynamics 365 integration.

**Time Required: 20-30 minutes**
**Cost: $0 (completely free)**

---

## Step 1: Go to Azure Portal

1. Open browser: https://portal.azure.com
2. Login with your admin credentials

---

## Step 2: Create App Registration

1. In the search bar at top, type: **"App registrations"**
2. Click **"App registrations"** from results
3. Click **"+ New registration"** (blue button at top)
4. Fill in the form:
   - **Name:** `Farm Data Automation API`
   - **Supported account types:** Select **"Accounts in this organizational directory only"** (first option)
   - **Redirect URI:** Leave blank (don't select anything)
5. Click **"Register"** button at bottom

---

## Step 3: Get Credential #1 and #2 (Application ID & Tenant ID)

After clicking Register, you'll see the app overview page.

**Copy these two values and save them:**

### 📋 Credential #1: Application (client) ID
- Look for **"Application (client) ID"** on the overview page
- It looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- Click the copy icon next to it
- **Paste this somewhere safe (Notepad)**

### 📋 Credential #2: Directory (tenant) ID
- Look for **"Directory (tenant) ID"** on the same overview page
- It looks like: `f9e8d7c6-b5a4-3210-fedc-ba0987654321`
- Click the copy icon next to it
- **Paste this somewhere safe (Notepad)**

---

## Step 4: Create Client Secret (Credential #3)

1. In the left sidebar, click **"Certificates & secrets"**
2. Click **"+ New client secret"** (under "Client secrets" tab)
3. Fill in:
   - **Description:** `Farm Data Automation Secret`
   - **Expires:** Select **"24 months"** (or longest available)
4. Click **"Add"**

### 📋 Credential #3: Client Secret Value

**⚠️ CRITICAL: DO THIS IMMEDIATELY!**

5. You'll see a new row appear with your secret
6. In the **"Value"** column, you'll see a long string
7. Click the **copy icon** next to the value
8. **PASTE IT IMMEDIATELY into Notepad** - YOU CAN'T SEE IT AGAIN!
9. It looks like: `abc123~XYZ789.secretvalue_here-verylongstring`

**Don't close this page until you've saved the value!**

---

## Step 5: Grant Dynamics 365 Permissions

1. In the left sidebar, click **"API permissions"**
2. Click **"+ Add a permission"**
3. Click **"Dynamics CRM"** (scroll down if needed)
4. Select **"Delegated permissions"**
5. Check the box for **"user_impersonation"**
6. Click **"Add permissions"** at bottom
7. Click **"Grant admin consent for [Your Organization]"** (blue button at top)
8. Click **"Yes"** to confirm

You should see a green checkmark that says "Granted for [Your Organization]"

---

## Step 6: Add App User to Dynamics 365

1. Open your Dynamics 365 environment URL (e.g., https://yourorg.crm3.dynamics.com)
2. Click the **gear icon** (⚙️) in top right
3. Click **"Advanced Settings"**
4. Click **"Settings"** → **"Security"** → **"Users"**
5. Change view dropdown to **"Application Users"**
6. Click **"+ New"**
7. Change form type to **"Application User"**
8. Fill in:
   - **Application ID:** Paste your Application (client) ID from Step 3
   - Press Tab (it will auto-fill some fields)
   - **Full Name:** `Farm Data Automation API`
9. Click **"Save"**
10. Click **"Manage Roles"**
11. Check **"System Administrator"** (or a custom role with animal permissions)
12. Click **"OK"**
13. Click **"Save & Close"**

---

## ✅ You're Done! Here Are Your 3 Credentials:

You should now have these 3 values saved in Notepad:

```
Application (client) ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Directory (tenant) ID: f9e8d7c6-b5a4-3210-fedc-ba0987654321
Client Secret: abc123~XYZ789.secretvalue_here-verylongstring
```

---

## 🔧 What to Do with These Credentials

Now update your database with these values:

### Option 1: Update via SQL (Quickest)

```sql
UPDATE clients
SET
    dynamics_client_id = 'PASTE_YOUR_APPLICATION_ID_HERE',
    dynamics_client_secret = 'PASTE_YOUR_CLIENT_SECRET_HERE',
    dynamics_tenant_id = 'PASTE_YOUR_TENANT_ID_HERE'
WHERE name = 'Demo Farm';
```

### Option 2: Update .env File

Create or update your `.env` file:

```bash
DYNAMICS_CLIENT_ID=PASTE_YOUR_APPLICATION_ID_HERE
DYNAMICS_CLIENT_SECRET=PASTE_YOUR_CLIENT_SECRET_HERE
DYNAMICS_TENANT_ID=PASTE_YOUR_TENANT_ID_HERE
```

---

## 🧪 Test It

After updating, restart your server and test a recording. It should now sync all the way to Dynamics 365!

---

**Total time: 15-20 minutes**
