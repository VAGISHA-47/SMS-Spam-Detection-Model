# SMS Spam Detection Model

SMS spam classifier using a pretrained scikit-learn model (`model.pkl` + `vectorizer.pkl`).

## Active deployment target
This repository is configured to deploy on **Vercel**.

- Static UI: `index.html`
- Python serverless API: `api/index.py`
- Vercel config: `vercel.json`

## Features
- Predict spam vs ham for SMS text
- Text preprocessing with NLTK
- Model metrics endpoint (`/api/metrics`)

## API routes
- `GET /api/health`
- `GET /api/models`
- `GET /api/metrics`
- `POST /api/predict`

Example request:

```bash
curl -X POST https://<your-vercel-domain>/api/predict \
  -H "content-type: application/json" \
  -d '{"text":"Congratulations! You won a free ticket"}'
```

## Deploy on Vercel
See full guide in [DEPLOYMENT.md](DEPLOYMENT.md).

Quick steps:
1. Push this repo to your GitHub account.
2. Import repository in Vercel: https://vercel.com/new
3. Deploy (Vercel uses `vercel.json` automatically).

## Local development

### Vercel local runtime
```bash
npm i -g vercel
vercel dev
```

### Streamlit app (optional local only)
The old Streamlit app is still present at `app.py` for local experimentation:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Required artifacts
Keep these files in project root:
- `model.pkl`
- `vectorizer.pkl`

## Environment variables
- `NEON_DB_URL` (optional, used by the Streamlit database path)
