# SMS Spam Detection

## Overview
SMS Spam Detection is a machine learning model that takes an SMS as input and predicts whether the message is a spam or not spam message. The model is built using Python and deployed on the web using Streamlit.

## Technology Used
- Python
- Scikit-learn
- Pandas
- NumPy
- Streamlit

## Features
- Data collection
- Data cleaning and preprocessing
- Exploratory Data Analysis
- Model building and selection
- Web deployment using Streamlit

### Data Collection
The SMS Spam Collection dataset was collected from Kaggle, which contains over 5,500 SMS messages labeled as either spam or not spam.
You can access the dataset from [here](https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset)

### Data Cleaning and Preprocessing
The data was cleaned by handling null and duplicate values, and the "type" column was label-encoded. The data was then preprocessed by converting the text into tokens, removing special characters, stop words and punctuation, and stemming the data. The data was also converted to lowercase before preprocessing.

### Exploratory Data Analysis
Exploratory Data Analysis was performed to gain insights into the dataset. The count of characters, words, and sentences was calculated for each message. The correlation between variables was also calculated, and visualizations were created using pyplots, bar charts, pie charts, 5 number summaries, and heatmaps. Word clouds were also created for spam and non-spam messages, and the most frequent words in spam texts were visualized.

### Model Building and Selection
Multiple classifier models were tried, including NaiveBayes, random forest, KNN, decision tree, logistic regression, ExtraTreesClassifier, and SVC. The best classifier was chosen based on precision, with a precision of 100% achieved.

### Web Deployment
The model was deployed on the web using Streamlit. The user interface has a simple input box where the user can input a message, and the model will predict whether it is spam or not spam.

## Usage
To use the SMS Spam Detection model on your own machine, follow these steps:

+ Clone this repository.
+ Install the required Python packages using 
```
pip install -r requirements.txt.
# SMS Spam Detection

A simple Streamlit app that predicts whether an SMS is spam or not using a pretrained scikit-learn model. This project includes a lightweight signup/login flow and per-user prediction history stored in MongoDB (with an in-memory fallback when Mongo is not configured).

This repository contains:
- `app.py` — Streamlit application with signup/login and prediction UI.
- `db.py` — Database helpers: connects to MongoDB (if `MONGO_URI` provided) and falls back to an in-memory store when unavailable.
- `vectorizer.pkl`, `model.pkl` — pretrained model artifacts (must be provided by you).
- `Dockerfile` and `render.yaml` — for containerized deployment (Render or other Docker hosts).
- `scripts/create_test_user.py` — convenience script to seed a test user.

## Features
- Spam detection using a pretrained scikit-learn model.
- Signup and login with password hashing (`werkzeug.security`).
- Per-user prediction history persisted to MongoDB (collection: `history`) when `MONGO_URI` is configured; otherwise stored in memory for the current session.
- Robust startup handling for NLTK resources (the app attempts to download missing data; Dockerfile pre-downloads them in the image).

## Quickstart (local)

1. Clone the repo and create a Python virtual environment:

```bash
git clone <your-repo-url>
cd SMS-Spam-Detection-Model
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add model artifacts:

Place `model.pkl` and `vectorizer.pkl` in the project root. The app will fail to predict without these files.

4. (Optional) Configure MongoDB:

If you want persistent history across restarts, set `MONGO_URI` in environment variables or a `.env` file. An example `.env.example` is included.

```bash
cp .env.example .env
# edit .env and set MONGO_URI to your connection string
```

If `MONGO_URI` is not set or MongoDB is unreachable, the app uses an in-memory fallback (history will not persist after restart).

5. Run the app locally:

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Create a test user (skip UI signup)

Use the helper script to create a user in MongoDB or in-memory (depending on `MONGO_URI`):

```bash
python scripts/create_test_user.py --username testuser --password secret
```

## Deploy with Docker (Render or other hosts)

A `Dockerfile` is included to produce a reproducible container image. The image pre-installs dependencies and pre-downloads necessary NLTK data.

Build and run locally:

```bash
# build
docker build -t sms-spam-app .
# run
docker run -p 8501:8501 -e PORT=8501 sms-spam-app
```

### Deploy to Render

- Push the repository to GitHub.
- On Render, create a new **Web Service** and connect your repo.
- Select **Docker** as the environment so Render uses the included `Dockerfile`.
- Optionally set the Start Command (the Dockerfile already defines a CMD):

```
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

- Add environment variables in the Render dashboard (recommended):
	- `MONGO_URI` — MongoDB connection string (Atlas or other).
	- Optionally `SECRET_KEY`, `PYTHONUNBUFFERED=1`.

The repo includes `render.yaml` which can be used to preconfigure a Render service.

## Environment variables
- `MONGO_URI` — (optional) MongoDB connection string. If unset or unreachable the app uses an in-memory fallback.
- `PORT` — provided by hosts like Render; Streamlit command uses `$PORT`.
- `PYTHONUNBUFFERED` — optional; set to `1` to keep logs unbuffered.
- `SECRET_KEY` — optional secret for future session/cookie features.

## Notes and security
- Use a managed MongoDB provider (like MongoDB Atlas) in production; do not expose local MongoDB to the public internet.
- Keep credentials out of source control — use platform secrets or environment variables.
- Ensure `model.pkl` and `vectorizer.pkl` are present in the repo when deploying.

## Troubleshooting
- NLTK LookupError on startup: run the following locally to fetch missing data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"
```

- If the app fails to connect to MongoDB at runtime, it will automatically fall back to an in-memory store. Check your `MONGO_URI` and network settings if you expect persistent storage.

## Development notes
- `db.py` centralizes DB behavior. It attempts to connect to MongoDB and sets an internal state; all helper functions gracefully fall back to session-level storage when Mongo is not available.
- `app.py` implements the Streamlit UI, including authentication and the prediction workflow. It uses `transform_text()` for preprocessing (NLTK + PorterStemmer) and loads the pretrained `vectorizer.pkl` and `model.pkl`.

## Contributing
Contributions are welcome. Open an issue or a pull request with proposed changes.

---

If you'd like, I can also prepare a minimal GitHub Actions workflow to build the Docker image and push to a container registry automatically when you push to `main`.


