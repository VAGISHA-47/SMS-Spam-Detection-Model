import os
import pickle
import string
from pathlib import Path

import nltk
import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

from neon_db import authenticate_user, create_user, get_user_predictions, init_db, save_prediction


st.set_page_config(page_title="SMS Spam Detection")


@st.cache_resource
def setup_nltk():
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)


ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()


def transform_text(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)

    tokens = nltk.word_tokenize(text.lower())
    toks = [token for token in tokens if token.isalnum()]

    stop_words = set(stopwords.words("english"))
    toks = [token for token in toks if token not in stop_words and token not in string.punctuation]

    out = [ps.stem(lemmatizer.lemmatize(token)) for token in toks]
    return " ".join(out)


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


def trigger_rerun() -> None:
    """Rerun the app in a Streamlit-version-safe way."""
    rerun_fn = getattr(st, "rerun", None)
    if callable(rerun_fn):
        rerun_fn()
    else:
        st.experimental_rerun()

db_ready = True
if not os.getenv("NEON_DB_URL"):
    db_ready = False
    st.warning("NEON_DB_URL is not set. Sign-in and history are disabled.")
else:
    try:
        init_db()
    except Exception as error:
        db_ready = False
        st.error(f"Database init failed: {error}")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None

with st.sidebar:
    st.markdown("## Account")
    if db_ready:
        if not st.session_state["logged_in"]:
            auth_choice = st.radio("Select action:", ["Login", "Sign up"])
            email = st.text_input("Email", key="sidebar_email")
            password = st.text_input("Password", type="password", key="sidebar_password")
            if auth_choice == "Sign up":
                if st.button("Create account", key="signup_btn"):
                    ok, msg = create_user(email, password)
                    if not ok:
                        st.error(msg)
                    else:
                        st.success("Account created. Please log in.")
            else:
                if st.button("Log in", key="login_btn"):
                    if authenticate_user(email, password):
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = email.strip().lower()
                        trigger_rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            st.success(f"Signed in as: {st.session_state['user_email']}")
            if st.button("Log out", key="logout_btn"):
                st.session_state["logged_in"] = False
                st.session_state["user_email"] = None
                trigger_rerun()
    else:
        st.info("Set NEON_DB_URL to enable accounts and history.")

st.title("SMS Spam Detection")

message = st.text_input("Enter message")

if st.button("Predict"):
    if not message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            cleaned_message = transform_text(message)
            transformed_input = vectorizer.transform([cleaned_message])
            prediction = model.predict(transformed_input)[0]

            if int(prediction) == 1:
                st.error("Spam")
            else:
                st.success("Not Spam")

            if db_ready and st.session_state.get("logged_in"):
                label = "spam" if int(prediction) == 1 else "not_spam"
                steps = {"transformed": cleaned_message}
                ok = save_prediction(
                    st.session_state["user_email"],
                    message,
                    cleaned_message,
                    steps,
                    int(prediction),
                    label,
                )
                if not ok:
                    st.warning("Prediction was not saved to history.")
        except Exception as error:
            st.error(f"Prediction failed: {error}")

if db_ready and st.session_state.get("logged_in"):
    st.subheader("Your History")
    items = get_user_predictions(st.session_state["user_email"], limit=20)
    if not items:
        st.info("No prediction history found.")
    else:
        for item in items:
            label = str(item.get("label", "n/a")).upper()
            text = item.get("text", "")
            ts = item.get("timestamp", "")
            st.write(f"**{label}** — {text} — {ts}")
