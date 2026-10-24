# LionPath — Render Deployment Guide (Production Web Service)

This guide walks you through deploying **LionPath** to the cloud on **Render (render.com)** for free. Once deployed, you will get a live public URL (e.g. `https://lionpath.onrender.com`) that you can open on any phone, share with your project supervisor, and present during your final year project defense.

---

## 1. Prerequisites Prepared in Your Codebase

Your repository has already been pre-configured with all Render production requirements:
- `requirements.txt`: Includes `Flask`, `gunicorn`, `spacy`, `thefuzz`, and `SQLAlchemy`.
- `Procfile`: Configured with `web: gunicorn app:app`.
- `render.yaml`: Automated blueprint specification file.
- `seed.py`: Automatically runs during build to initialize the 16 campus landmarks, 32 walking routes, 17 FAQs, and timetables.
- `app.py`: Configured to bind dynamically to `host="0.0.0.0"` and `port=$PORT`.

---

## 2. Push Your Code to GitHub

If you haven't already pushed your code to GitHub, run these commands in PowerShell inside your project folder:

```powershell
# Initialize git (if not already done)
git init

# Add all project files
git add .

# Commit changes
git commit -m "LionPath Final Year Project - Production Ready"

# Rename default branch to main
git branch -M main

# Link to your GitHub repository (replace with your actual GitHub repo URL)
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/lionpath.git

# Push code to GitHub
git push -u origin main
```

---

## 3. Deploy on Render (Free Tier)

### Method A: 1-Click Blueprint (Recommended)
1. Go to [https://dashboard.render.com/](https://dashboard.render.com/) and log in (or sign up with your GitHub account).
2. Click the **"New +"** button at the top right, then select **"Blueprint"**.
3. Connect your GitHub account and select your **`lionpath`** repository.
4. Render will automatically detect [`render.yaml`](file:///c:/Users/user/OneDrive/Desktop/lionpath/render.yaml) and pre-fill all configurations:
   - **Service Name**: `lionpath`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `gunicorn app:app`
5. Click **"Apply"**.
6. Render will build the virtual environment, seed the SQLite database, and launch the service in ~2-3 minutes.

---

### Method B: Manual Web Service
If you prefer configuring it manually without Blueprint:
1. On Render Dashboard, click **"New +"** $\rightarrow$ **"Web Service"**.
2. Select your `lionpath` repository.
3. Fill in the fields:
   - **Name**: `lionpath` (or any custom name)
   - **Region**: Choose the closest region (e.g., *Frankfurt* or *Oregon*)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python seed.py`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: **Free**
4. Scroll down to **"Environment Variables"** and click **"Add Environment Variable"**:
   - `ADMIN_USERNAME` = `admin`
   - `ADMIN_PASSWORD` = `lionpath2026`
   - `SECRET_KEY` = `lionpath-unn-2026-secret-key`
   - `FLASK_DEBUG` = `False`
5. Click **"Deploy Web Service"**.

---

## 4. Accessing Your Live System

Once the deployment completes:
- **Chatbot Public URL**: `https://<your-service-name>.onrender.com`
- **Admin Dashboard**: `https://<your-service-name>.onrender.com/admin`
  - **Username**: `admin`
  - **Password**: `lionpath2026`
- **Interactive Campus Map**: Click the **"🗺️ Campus Map"** button on the live site!

---

## 5. Defense Demo Tips

- **Mobile Presentation**: Open `https://<your-service-name>.onrender.com` directly on your mobile browser during your defense. You can hand your phone to the examiners to let them test it live!
- **Voice Input**: The Web Speech Recognition microphone (`🎤`) works over HTTPS on modern mobile browsers (Chrome on Android, Safari on iOS).
- **Cold Starts**: Render's free tier spins down after 15 minutes of inactivity. Open your URL 2 minutes before your defense starts so the server is warm and responds instantly.

