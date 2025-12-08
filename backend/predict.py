#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import re


def transform_text(text):
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    # step 1: lowercase and tokenize
    raw = text
    lower = text.lower()
    tokens = nltk.word_tokenize(lower)
    # step 2: keep alnum tokens
    tokens_alpha = [re.sub(r"[^a-z0-9]", "", t) for t in tokens]
    tokens_alpha = [t for t in tokens_alpha if t]
    # step 3: remove stopwords
    stop = set(stopwords.words('english'))
    after_stop = [t for t in tokens_alpha if t not in stop]
    # step 4: lemmatize then stem
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    after_lemmatize = [lemmatizer.lemmatize(t) for t in after_stop]
    after_stem = [stemmer.stem(t) for t in after_lemmatize]
    transformed = ' '.join(after_stem)
    # return structured steps
    return {
        'raw': raw,
        'lower': lower,
        'tokens': tokens,
        'tokens_alpha': tokens_alpha,
        'after_stop': after_stop,
        'after_lemmatize': after_lemmatize,
        'after_stem': after_stem,
        'transformed': transformed
    }


def load_artifacts(model_name=None):
    # default names
    vector_path = root / 'vectorizer.pkl'
    model_path = root / 'model.pkl'
    # allow alternate names like model_nb.pkl
    if model_name and model_name not in ('model', 'vectorizer'):
        cand1 = root / f'vectorizer_{model_name}.pkl'
        cand2 = root / f'{model_name}.pkl'
        if cand1.exists():
            vector_path = cand1
        if cand2.exists():
            model_path = cand2
    vec = joblib.load(vector_path)
    m = joblib.load(model_path)
    return vec, m


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', type=str, required=True)
    parser.add_argument('--model', type=str, default='default')
    args = parser.parse_args()

    vec, m = load_artifacts(args.model)
    steps = transform_text(args.text)
    transformed = steps['transformed']
    X = vec.transform([transformed])
    pred = m.predict(X)[0]
    probs = None
    try:
        probs = m.predict_proba(X).tolist()[0]
    except Exception:
        probs = None

    out = {
        'input': args.text,
        'transformed': transformed,
        'steps': steps,
        'prediction': int(pred) if hasattr(pred, '__int__') else pred,
        'probabilities': probs
    }
    print(json.dumps(out))


if __name__ == '__main__':
    main()
