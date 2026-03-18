import json
import re
from pathlib import Path

from flask import Flask, jsonify, request
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer


app = Flask(__name__)

ROOT = Path(__file__).resolve().parent.parent
VECTORIZER_PATH = ROOT / "vectorizer.pkl"
MODEL_PATH = ROOT / "model.pkl"
METRICS_PATH = ROOT / "metrics.json"


def _ensure_nltk_data():
    packages = ["punkt", "stopwords", "wordnet", "omw-1.4"]
    for package in packages:
        try:
            if package == "punkt":
                nltk.data.find("tokenizers/punkt")
            else:
                nltk.data.find(f"corpora/{package}")
        except LookupError:
            nltk.download(package, quiet=True)


_ensure_nltk_data()
VECTORIZER = joblib.load(VECTORIZER_PATH)
MODEL = joblib.load(MODEL_PATH)


def transform_text(text: str):
    lower = text.lower()
    tokens = nltk.word_tokenize(lower)
    tokens_alpha = [re.sub(r"[^a-z0-9]", "", token) for token in tokens]
    tokens_alpha = [token for token in tokens_alpha if token]

    stop_words = set(stopwords.words("english"))
    after_stop = [token for token in tokens_alpha if token not in stop_words]

    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    after_lemmatize = [lemmatizer.lemmatize(token) for token in after_stop]
    after_stem = [stemmer.stem(token) for token in after_lemmatize]
    transformed = " ".join(after_stem)

    return {
        "raw": text,
        "lower": lower,
        "tokens": tokens,
        "tokens_alpha": tokens_alpha,
        "after_stop": after_stop,
        "after_lemmatize": after_lemmatize,
        "after_stem": after_stem,
        "transformed": transformed,
    }


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/models")
def models():
    names = []
    for file in ROOT.iterdir():
        if file.suffix in {".pkl", ".joblib"}:
            names.append(file.stem)
    if not names:
        names = ["model"]
    return jsonify({"models": sorted(names)})


@app.get("/api/metrics")
def metrics():
    if not METRICS_PATH.exists():
        return jsonify({"error": "metrics.json not found"}), 404
    with METRICS_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)
    return jsonify(data)


@app.post("/api/predict")
def predict():
    body = request.get_json(silent=True) or {}
    text = (body.get("text") or "").strip()

    if not text:
        return jsonify({"error": "text is required"}), 400

    steps = transform_text(text)
    transformed = steps["transformed"]
    vector = VECTORIZER.transform([transformed])
    prediction = MODEL.predict(vector)[0]

    probabilities = None
    try:
        probabilities = MODEL.predict_proba(vector).tolist()[0]
    except Exception:
        probabilities = None

    return jsonify(
        {
            "input": text,
            "transformed": transformed,
            "steps": steps,
            "prediction": int(prediction) if hasattr(prediction, "__int__") else prediction,
            "probabilities": probabilities,
        }
    )
