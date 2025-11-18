# Deployment Guide

## ⚠️ SECURITY CRITICAL

**NEVER commit your `.env` file or API keys to git!**

The `.gitignore` file is already configured to prevent this, but always double-check before pushing.

---

## Local Development Setup (Updated)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create `.env` file** (already exists, just edit it):
   ```
   ANTHROPIC_API_KEY=your-actual-key-here
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

The app will automatically load the key from `.env` - no need to set environment variables manually!

---

## Deployment Options

### Option 1: Heroku (Easiest)

1. **Install Heroku CLI** and login
2. **Create a Procfile:**
   ```
   web: gunicorn app:app
   ```
3. **Add gunicorn to requirements.txt:**
   ```bash
   pip install gunicorn
   pip freeze > requirements.txt
   ```
4. **Deploy:**
   ```bash
   heroku create your-app-name
   heroku config:set ANTHROPIC_API_KEY=your-key-here
   git push heroku main
   ```

### Option 2: Render (Free Tier Available)

1. Push code to GitHub (without .env!)
2. Create new Web Service on Render.com
3. Connect your GitHub repo
4. Set environment variable:
   - Key: `ANTHROPIC_API_KEY`
   - Value: your API key
5. Deploy!

### Option 3: Railway

1. Push to GitHub
2. Create new project on Railway.app
3. Connect repo
4. Add environment variable `ANTHROPIC_API_KEY`
5. Deploy automatically

### Option 4: DigitalOcean App Platform

1. Push to GitHub
2. Create new App
3. Select your repo
4. Add environment variable in Settings
5. Deploy

### Option 5: AWS/Azure/GCP

For production-grade deployment, you'd want:
- AWS: Elastic Beanstalk or ECS
- Azure: App Service
- GCP: Cloud Run

Set environment variables through their respective consoles/CLI.

---

## Important Deployment Considerations

### 🔒 Security (CRITICAL for public deployment)

This app currently has **NO authentication**. Before deploying publicly, ADD:

1. **User authentication** (login system)
2. **Rate limiting** (prevent API abuse)
3. **HTTPS only** (most platforms do this automatically)
4. **API key rotation** (change keys periodically)

### 💰 Cost Management

Set up **billing alerts** in Anthropic Console:
- Set monthly spending limit
- Get email alerts at thresholds

### 📊 For Production Use

Consider adding:
- Database (save grades, not just display)
- User accounts (multiple teachers)
- Batch processing queue
- Usage analytics
- Admin dashboard

---

## Quick Test Deployment (Private)

**Easiest option for testing:**

1. Keep running locally
2. Use **ngrok** to expose to internet temporarily:
   ```bash
   ngrok http 5000
   ```
3. Share the ngrok URL (valid for a few hours)
4. Perfect for showing colleagues or testing on phone

---

## Environment Variables on Each Platform

| Platform | How to Set Env Vars |
|----------|-------------------|
| **Heroku** | `heroku config:set KEY=value` |
| **Render** | Dashboard → Environment tab |
| **Railway** | Dashboard → Variables |
| **Vercel** | Dashboard → Settings → Environment Variables |
| **DigitalOcean** | App Settings → Environment Variables |

**Never set environment variables in code or commit them to git!**

---

## Recommended First Deployment: Render

**Why Render:**
- Free tier available
- Easy setup
- Automatic HTTPS
- Simple environment variable management
- No credit card required for free tier

**Steps:**
1. Push code to GitHub (make sure .env is NOT included!)
2. Go to render.com
3. New → Web Service
4. Connect GitHub repo
5. Set `ANTHROPIC_API_KEY` in environment
6. Click Deploy

**Takes ~5 minutes total!**

---

## Testing Before Deployment

Always test locally with `.env` first:
```bash
pip install -r requirements.txt
python app.py
```

If it works locally with `.env`, it'll work deployed with environment variables!
