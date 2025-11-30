import os
import nltk

def ensure_nltk_resources():
    """Ensure necessary NLTK resources are available; download if missing."""
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/stopwords', 'stopwords'),
    ]
    for path, name in resources:
        try:
            nltk.data.find(path)
        except Exception:
            try:
                nltk.download(name)
            except Exception:
                # best effort: ignore download failures here
                pass


ensure_nltk_resources()

import streamlit as st
import pickle
import string
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

from db import create_user, authenticate, save_history, get_history, DB_CONNECTED

ps = PorterStemmer()

# Ensure session key exists so checks are reliable across runs
import streamlit as _st_init
if 'user' not in _st_init.session_state:
    _st_init.session_state['user'] = None


def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stopwords.words('english') and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)


# Load ML artifacts
tk = pickle.load(open("vectorizer.pkl", 'rb'))
model = pickle.load(open("model.pkl", 'rb'))


# DB helpers are centralized in `db.py` (with in-memory fallbacks there)



# Header / top bar
with st.container():
    hcol, scol = st.columns([4, 1])
    with hcol:
        st.title("SMS Spam Detection Model")


def show_login():
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            # basic validation
            if not username or not password:
                st.error("Username and password required")
            else:
                if authenticate(username, password):
                    st.session_state['user'] = username
                    st.success("Logged in as %s" % username)
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")


def show_signup():
    st.subheader("Sign up")
    with st.form("signup_form"):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        submitted = st.form_submit_button("Sign up")
        if submitted:
            if not username or not password:
                st.error("Username and password required")
            elif create_user(username, password):
                # Auto-login after successful signup
                st.session_state['user'] = username
                st.success("User created and logged in as %s" % username)
                st.experimental_rerun()
            else:
                st.error("Username already exists")


if 'user' not in st.session_state or not st.session_state.get('user'):
    tabs = st.tabs(["Login", "Sign up"])
    with tabs[0]:
        show_login()
    with tabs[1]:
        show_signup()
    st.stop()


# Main app for logged in users
username = st.session_state.get('user')
# Main app for logged in users
# Main app for logged in users
username = st.session_state.get('user')
st.write(f"**Logged in as:** {username}")
if st.button('Logout'):
    st.session_state['user'] = None
    st.experimental_rerun()


input_sms = st.text_area("Enter the SMS")

if st.button('Predict'):

    if not input_sms or input_sms.strip() == "":
        st.warning("Please enter a message to analyze")
    else:
        transformed_sms = transform_text(input_sms)
        vector_input = tk.transform([transformed_sms])
        result = model.predict(vector_input)[0]
        label = 'Spam' if result == 1 else 'Not Spam'
        st.header(label)
        # Save history
        save_history(username, input_sms, label)


if st.button('View History'):
    records = get_history(username)
    if not records:
        st.info("No history yet")
    else:
        df = pd.DataFrame([{'message': r['message'], 'label': r['label'], 'timestamp': r['timestamp']} for r in records])
        st.dataframe(df)

