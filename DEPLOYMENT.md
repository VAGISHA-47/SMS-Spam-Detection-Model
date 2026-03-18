# Deploying to Vercel

This project is now configured for **Vercel deployment** using:
- Static frontend: `index.html`
- Python serverless API: `api/index.py`

## Prerequisites
1. GitHub account
2. Vercel account
3. Project pushed to your own repository

## Files used by Vercel
- `vercel.json` — routing and build config
- `index.html` — frontend UI
- `api/index.py` — API endpoints
- `requirements.txt` — Python dependencies
- `model.pkl`, `vectorizer.pkl` — ML artifacts

## API Endpoints
- `GET /api/health`
- `GET /api/models`
- `GET /api/metrics`
- `POST /api/predict`

## Step-by-step deployment

### 1) Push to your GitHub repository
```bash
git add .
git commit -m "Configure Vercel deployment"
git push origin main
```

### 2) Import project in Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Framework preset: **Other**
4. Keep default build settings (Vercel reads `vercel.json`)
5. Click **Deploy**

### 3) Verify deployment
After deploy succeeds:
- Open your Vercel URL and test prediction from UI.
- Check health endpoint:
  - `https://<your-project>.vercel.app/api/health`

## Local verification (optional)
Install Vercel CLI and run:
```bash
vercel dev
```
Then open local URL and test `/api/predict`.

## Notes
- Streamlit Cloud deployment instructions are intentionally removed.
- This Vercel setup does not depend on Streamlit runtime.
- Keep `model.pkl` and `vectorizer.pkl` in repo root for API inference.
