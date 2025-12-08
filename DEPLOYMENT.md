# Deploying to Streamlit Cloud

## Prerequisites
1. GitHub account
2. Streamlit Cloud account (sign up at https://share.streamlit.io)
3. (Optional) Neon PostgreSQL database for user accounts

## Step-by-Step Deployment Guide

### 1. Push Your Code to GitHub
Your code is already on GitHub at: `https://github.com/sidhu90989/SMS-Spam-Detection-Model`

### 2. Sign Up / Log In to Streamlit Cloud
- Go to: https://share.streamlit.io
- Sign in with your GitHub account

### 3. Deploy New App
1. Click "New app" button
2. Select your repository: `sidhu90989/SMS-Spam-Detection-Model`
3. Branch: `main`
4. Main file path: `app.py`
5. App URL: Choose a custom URL (e.g., `sms-spam-detector`)

### 4. Configure Secrets (Optional - For Database)
If you want user accounts and history, add your database connection:

1. Click "Advanced settings"
2. In the "Secrets" section, add:
```toml
NEON_DB_URL = "postgresql://username:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

**Note:** The app works without a database in demo mode! Users can still classify SMS messages.

### 5. Deploy!
Click "Deploy" and wait for the app to build and start.

## Getting a Free PostgreSQL Database (Optional)

### Option 1: Neon (Recommended)
1. Go to: https://neon.tech
2. Sign up for free account
3. Create a new project
4. Copy the connection string
5. Add it to Streamlit secrets as shown above

### Option 2: Supabase
1. Go to: https://supabase.com
2. Create a new project
3. Get the connection string from Settings > Database
4. Add it to Streamlit secrets

### Option 3: ElephantSQL
1. Go to: https://www.elephantsql.com
2. Create a free Tiny Turtle instance
3. Copy the connection URL
4. Add it to Streamlit secrets

## App Features

### With Database:
- ✅ User signup and login
- ✅ SMS spam detection
- ✅ Prediction history per user
- ✅ Persistent data storage

### Without Database (Demo Mode):
- ✅ SMS spam detection
- ⚠️ No user accounts
- ⚠️ No history tracking

## Troubleshooting

### Build Fails
- Check that all files are committed and pushed to GitHub
- Verify `requirements.txt` is present
- Check Streamlit Cloud logs for specific errors

### Database Connection Issues
- Verify `NEON_DB_URL` is correctly set in Streamlit secrets
- Ensure the connection string includes `?sslmode=require`
- Check database is accessible (not behind firewall)

### NLTK Data Not Found
- Already handled in code with `nltk.download()` calls
- If issues persist, check the logs

## Files Required for Deployment

✅ All files are present and ready:
- `app.py` - Main application
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependencies
- `model.pkl` - Trained model
- `vectorizer.pkl` - TF-IDF vectorizer
- `train_model.py` - Helper functions
- `neon_db.py` - Database functions
- `.streamlit/config.toml` - Streamlit configuration

## Post-Deployment

After successful deployment:
1. Test the app thoroughly
2. Share the URL with users
3. Monitor app performance in Streamlit Cloud dashboard
4. Check logs for any runtime errors

## Updating Your App

To update the deployed app:
1. Make changes locally
2. Commit and push to GitHub
3. Streamlit Cloud will automatically rebuild and redeploy

## Support

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Community: https://discuss.streamlit.io
- GitHub Issues: Create an issue in your repository
