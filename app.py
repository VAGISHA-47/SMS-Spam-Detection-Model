import pickle
from pathlib import Path

import nltk
import streamlit as st


st.set_page_config(page_title="SMS Spam Detection")


@st.cache_resource
def setup_nltk():
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)


@st.cache_resource
def load_artifacts():
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / "model.pkl"
    vectorizer_path = base_dir / "vectorizer.pkl"

    if not model_path.exists() or not vectorizer_path.exists():
        st.error("model.pkl or vectorizer.pkl not found in project root.")
        st.stop()

    try:
        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)
        with open(vectorizer_path, "rb") as vectorizer_file:
            vectorizer = pickle.load(vectorizer_file)
        return model, vectorizer
    except Exception as error:
        st.error(f"Failed to load model artifacts: {error}")
        st.stop()


setup_nltk()
model, vectorizer = load_artifacts()

st.title("SMS Spam Detection")

message = st.text_input("Enter message")

if st.button("Predict"):
    if not message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            transformed_input = vectorizer.transform([message])
            prediction = model.predict(transformed_input)[0]

            if int(prediction) == 1:
                st.error("Spam")
            else:
                st.success("Not Spam")
        except Exception as error:
            st.error(f"Prediction failed: {error}")
