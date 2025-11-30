FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV NLTK_DATA=/usr/share/nltk_data

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y --no-install-recommends build-essential wget && \
    python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get remove -y build-essential && apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Pre-download common NLTK data so runtime doesn't have to fetch it
RUN python - <<'PY'
import nltk
try:
    nltk.download('punkt', download_dir='/usr/share/nltk_data')
except Exception:
    pass
try:
    nltk.download('stopwords', download_dir='/usr/share/nltk_data')
except Exception:
    pass
try:
    nltk.download('punkt_tab', download_dir='/usr/share/nltk_data')
except Exception:
    pass
PY

COPY . /app

EXPOSE 8501

# Start Streamlit using the port Render provides in $PORT
CMD streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
