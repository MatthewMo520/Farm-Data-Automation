# Complete Hosting Guide - Deploy Your Farm Data Automation System

This guide shows you how to host the entire application from scratch. Choose the option that fits your needs!

---

## Hosting Options Overview

| Option | Cost | Difficulty | Best For |
|--------|------|------------|----------|
| **Local Server** | FREE | Easy | Testing, MVP, single location |
| **Railway.app** | FREE tier available | Easy | Quick cloud deployment |
| **Render.com** | FREE tier available | Easy | Simple cloud hosting |
| **DigitalOcean** | $6/month | Medium | Full control, production |
| **AWS/Azure** | ~$10-20/month | Hard | Enterprise, scalability |

**Recommendation for Farms: Start with Local Server or Railway.app**

---

## Option 1: Local Server (FREE - Easiest)

Run on your own computer or farm office server.

### Requirements
- Windows, Mac, or Linux computer
- Python 3.11+
- Internet connection (for initial setup)

### Step 1: Install Python

**Windows:**
1. Download from: https://www.python.org/downloads/
2. Run installer
3. ✅ **Check "Add Python to PATH"**
4. Click "Install Now"

**Mac:**
```bash
brew install python@3.11
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv
```

### Step 2: Clone Repository

```bash
# Navigate to where you want the project
cd C:\Projects  # Windows
cd ~/Projects   # Mac/Linux

# Clone from GitHub (if you have the repo URL)
git clone https://github.com/yourusername/Farm-Data-Automation.git
cd Farm-Data-Automation

# OR download ZIP from GitHub and extract it
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will take 2-5 minutes and install all packages.

### Step 5: Create .env File

1. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env  # Mac/Linux
   copy .env.example .env  # Windows
   ```

2. Edit `.env` file with your values (see **API_SETUP_GUIDE.md**)

### Step 6: Initialize Database

```bash
# Run the seed script to create demo client
python scripts/seed_demo_client.py
```

### Step 7: Start the Server

```bash
python -m backend.main
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 8: Access the Application

1. Open browser: http://localhost:8000
2. Login with demo credentials
3. Start using!

### Running on Startup (Windows)

Create a batch file `start_server.bat`:
```batch
@echo off
cd C:\Path\To\Farm-Data-Automation
call venv\Scripts\activate
python -m backend.main
```

**Add to Windows Startup:**
1. Press `Win + R`
2. Type: `shell:startup`
3. Create shortcut to `start_server.bat`

### Running on Startup (Mac/Linux)

Create systemd service `/etc/systemd/system/farm-automation.service`:
```ini
[Unit]
Description=Farm Data Automation
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername/Farm-Data-Automation
ExecStart=/home/yourusername/Farm-Data-Automation/venv/bin/python -m backend.main
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable farm-automation
sudo systemctl start farm-automation
```

### Access from Other Devices on Network

Find your computer's IP address:

**Windows:**
```bash
ipconfig
# Look for "IPv4 Address" - e.g., 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig
# Look for "inet" - e.g., 192.168.1.100
```

Access from other devices: `http://192.168.1.100:8000`

**Pros:**
- ✅ 100% FREE
- ✅ Full control
- ✅ No internet required (after setup)
- ✅ Fast (local network)

**Cons:**
- ❌ Not accessible outside your network
- ❌ Computer must stay on
- ❌ You manage backups

---

## Option 2: Railway.app (FREE Tier - Easiest Cloud)

Railway offers 500 hours/month FREE - perfect for farms!

### Step 1: Create Railway Account

1. Go to: https://railway.app/
2. Click **"Start a New Project"**
3. Sign up with GitHub (recommended) or email
4. Verify your email

### Step 2: Push Code to GitHub

**If you haven't already:**
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Create repo on GitHub, then:
git remote add origin https://github.com/yourusername/Farm-Data-Automation.git
git push -u origin main
```

### Step 3: Deploy from GitHub

1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository
4. Railway will auto-detect it's a Python app

### Step 4: Add PostgreSQL Database

1. Click **"+ New"** in your project
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will create a free PostgreSQL database
4. Copy the `DATABASE_URL` from the database settings

### Step 5: Set Environment Variables

1. Click on your app service
2. Go to **"Variables"** tab
3. Add all your environment variables from `.env` file:
   - `GROQ_API_KEY`
   - `DYNAMICS_CLIENT_ID`
   - `DYNAMICS_CLIENT_SECRET`
   - `DYNAMICS_TENANT_ID`
   - `DYNAMICS_BASE_URL`
   - `SECRET_KEY`
   - `DATABASE_URL` (use the one from PostgreSQL database)
   - `ENVIRONMENT=production`
   - `WHISPER_MODE=local`
   - `WHISPER_LOCAL_MODEL=base`

### Step 6: Deploy

1. Railway will automatically deploy
2. Wait 2-5 minutes for build
3. Click on the generated URL (e.g., `your-app.railway.app`)

### Step 7: Initialize Database

Use Railway's terminal:
1. Click on your app
2. Go to **"Settings"** → **"Terminal"**
3. Run:
   ```bash
   python scripts/seed_demo_client.py
   ```

### Custom Domain (Optional)

1. Go to **"Settings"** → **"Domains"**
2. Add your custom domain (e.g., `farm.yourfarm.com`)
3. Update DNS settings as Railway instructs

### Free Tier Limits
- **500 hours/month** execution time
- **100GB** network egress
- **512MB RAM**
- Perfect for 1-10 users!

**Pros:**
- ✅ Easy deployment
- ✅ FREE tier available
- ✅ Auto-scaling
- ✅ HTTPS included
- ✅ GitHub auto-deploy

**Cons:**
- ❌ 500 hours/month limit (21 days of 24/7 uptime)
- ❌ Need GitHub account

---

## Option 3: Render.com (FREE Tier)

Similar to Railway, with different free tier limits.

### Step 1: Create Render Account

1. Go to: https://render.com/
2. Click **"Get Started"**
3. Sign up with GitHub or email

### Step 2: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Name: `farm-automation-db`
3. Select **"Free"** plan
4. Click **"Create Database"**
5. Copy the **"Internal Database URL"**

### Step 3: Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Fill in:
   - **Name:** `farm-automation`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Select **"Free"** plan

### Step 4: Set Environment Variables

In your web service settings:
1. Go to **"Environment"** tab
2. Add all variables from your `.env` file
3. Use the PostgreSQL `DATABASE_URL` you copied earlier

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy (5-10 minutes)
3. Access your app at the provided URL

### Step 6: Initialize Database

Use Render Shell:
1. Go to your web service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python scripts/seed_demo_client.py
   ```

### Free Tier Limits
- **750 hours/month** (more than Railway!)
- **100GB** bandwidth/month
- **512MB RAM**
- Spins down after 15 min of inactivity (cold starts)

**Pros:**
- ✅ More hours than Railway (750 vs 500)
- ✅ Easy to use
- ✅ HTTPS included
- ✅ Good documentation

**Cons:**
- ❌ Spins down when inactive (30s cold start)
- ❌ Slower build times than Railway

---

## Option 4: DigitalOcean Droplet ($6/month)

Full control with your own Linux server.

### Step 1: Create DigitalOcean Account

1. Go to: https://www.digitalocean.com/
2. Sign up and add payment method
3. Get $200 free credit (for new users)

### Step 2: Create Droplet

1. Click **"Create"** → **"Droplets"**
2. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($6/month - 1GB RAM)
   - **Region:** Closest to your farm
   - **Authentication:** SSH key (recommended) or password
3. Click **"Create Droplet"**

### Step 3: Connect to Server

```bash
ssh root@your-droplet-ip
```

### Step 4: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3.11 python3.11-venv python3-pip git nginx -y

# Install PostgreSQL
apt install postgresql postgresql-contrib -y
```

### Step 5: Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE farm_automation;
CREATE USER farmuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE farm_automation TO farmuser;
\q
```

### Step 6: Clone and Setup Application

```bash
# Create app user
adduser farmapp
su - farmapp

# Clone repository
git clone https://github.com/yourusername/Farm-Data-Automation.git
cd Farm-Data-Automation

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 7: Configure .env File

```bash
nano .env
```

Add all your environment variables:
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://farmuser:your_secure_password@localhost/farm_automation
# ... all other variables
```

### Step 8: Initialize Database

```bash
python scripts/seed_demo_client.py
```

### Step 9: Create Systemd Service

Exit farmapp user, then:
```bash
sudo nano /etc/systemd/system/farm-automation.service
```

Add:
```ini
[Unit]
Description=Farm Data Automation
After=network.target

[Service]
Type=simple
User=farmapp
WorkingDirectory=/home/farmapp/Farm-Data-Automation
Environment="PATH=/home/farmapp/Farm-Data-Automation/venv/bin"
ExecStart=/home/farmapp/Farm-Data-Automation/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable farm-automation
sudo systemctl start farm-automation
```

### Step 10: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/farm-automation
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/farm-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 11: Add SSL (HTTPS)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Access Your App

Visit: https://your-domain.com

**Pros:**
- ✅ Full control
- ✅ No time limits
- ✅ Can run 24/7
- ✅ Better performance
- ✅ Custom configuration

**Cons:**
- ❌ $6/month cost
- ❌ More technical
- ❌ You manage updates/security

---

## Option 5: Docker Deployment (Any Cloud)

Use Docker for consistent deployment anywhere.

### Dockerfile (Already Created)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create storage directory
RUN mkdir -p /app/storage/recordings

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Locally

```bash
# Build image
docker build -t farm-automation .

# Run container
docker run -d \
  --name farm-app \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/storage:/app/storage \
  farm-automation
```

### Deploy to Any Cloud

**Docker Hub:**
```bash
docker tag farm-automation yourusername/farm-automation
docker push yourusername/farm-automation
```

Then deploy to:
- **AWS ECS**
- **Google Cloud Run**
- **Azure Container Instances**
- **Any VPS with Docker**

---

## Choosing the Right Option

### For Testing/MVP
→ **Local Server** (FREE)

### For 1-5 Users, Cloud Access Needed
→ **Railway.app** (FREE tier)

### For 5-20 Users
→ **Render.com** ($7/month paid tier) or **Railway.app** (paid)

### For 20+ Users, Production
→ **DigitalOcean** ($12-24/month) or **AWS/Azure**

### For Multiple Farms/Locations
→ **DigitalOcean** or **AWS** with load balancer

---

## Database Backup (IMPORTANT!)

### Local SQLite Backup

```bash
# Manual backup
cp farm_data.db farm_data.db.backup

# Automated daily backup (Linux/Mac)
crontab -e
# Add: 0 2 * * * cp /path/to/farm_data.db /path/to/backups/farm_data_$(date +\%Y\%m\%d).db
```

### PostgreSQL Backup

```bash
# Manual backup
pg_dump -U farmuser farm_automation > backup.sql

# Restore
psql -U farmuser farm_automation < backup.sql

# Automated (add to cron)
0 2 * * * pg_dump -U farmuser farm_automation > /backups/farm_$(date +\%Y\%m\%d).sql
```

### Cloud Backups

**Railway/Render:**
- Use their built-in database backups
- Download backups weekly

**DigitalOcean:**
- Enable automated backups ($1.20/month)
- Or use custom backup scripts

---

## Monitoring and Maintenance

### Check Logs

**Local:**
```bash
# View real-time logs
python -m backend.main

# Or use systemd
sudo journalctl -u farm-automation -f
```

**Railway/Render:**
- View logs in web dashboard
- Set up log alerts

**DigitalOcean:**
```bash
sudo journalctl -u farm-automation -f
```

### Update Application

**Local/DigitalOcean:**
```bash
cd Farm-Data-Automation
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart farm-automation
```

**Railway/Render:**
- Push to GitHub
- Auto-deploys automatically

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set up firewall (UFW on Linux)
- [ ] Keep system updated
- [ ] Regular database backups
- [ ] Monitor API usage
- [ ] Limit SSH access (DigitalOcean)

---

## Cost Comparison

| Option | Monthly Cost | Suitable For |
|--------|-------------|--------------|
| Local Server | **$0** | Testing, 1 location |
| Railway.app (free) | **$0** | Up to 500 hours/month |
| Render.com (free) | **$0** | Up to 750 hours/month |
| Railway.app (paid) | **$5-10** | 24/7 uptime, small farm |
| Render.com (paid) | **$7** | 24/7 uptime |
| DigitalOcean | **$6-12** | Production, full control |
| AWS/Azure | **$10-30** | Enterprise, scaling |

---

## Need Help?

- **Railway Docs:** https://docs.railway.app/
- **Render Docs:** https://render.com/docs
- **DigitalOcean Docs:** https://docs.digitalocean.com/
- **Docker Docs:** https://docs.docker.com/

---

**Your application is now ready to be hosted anywhere!** 🚀

Choose the option that fits your budget and technical comfort level, and you'll be up and running!
