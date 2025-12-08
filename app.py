import streamlit as st
st.set_page_config(page_title='SMS Spam Detection', layout='wide')
import os
import datetime
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Project base dir
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# Load model/vectorizer
import joblib
vectorizer_path = BASE_DIR / 'vectorizer.pkl'
model_path = BASE_DIR / 'model.pkl'
tk = joblib.load(vectorizer_path)
model = joblib.load(model_path)

# Neon DB (PostgreSQL) connection
from neon_db import create_user, authenticate_user, save_prediction, get_user_predictions, init_db
try:
    init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")

# Helper function
from train_model import transform_text

# Ensure session state keys exist before any usage
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

st.title("SMS Spam Detection")

# --- Authentication UI (Sidebar) ---
with st.sidebar:
    st.markdown("## 🔒 Account")
    st.markdown("---")
    st.markdown("**Sign in or create an account to use the SMS Spam Detector and view your prediction history.**")
    st.markdown("")
    if not st.session_state['logged_in']:
        auth_choice = st.radio("Select action:", ["Login", "Sign up"])
        st.markdown("")
        email = st.text_input("Email", key="sidebar_email").strip().lower()
        password = st.text_input("Password", type="password", key="sidebar_password").strip()
        st.markdown("")
        if auth_choice == "Sign up":
            if st.button("Create account", key="signup_btn"):
                if not email or not password:
                    st.error("Email and password are required.")
                else:
                    ok, msg = create_user(email, password)
                    if not ok:
                        st.error(msg)
                    else:
                        st.success("Account created — signing you in now!")
                        # Auto-login after signup
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = email
                        st.experimental_rerun()
        else:
            if st.button("Log in", key="login_btn"):
                if not email or not password:
                    st.error("Email and password are required.")
                elif authenticate_user(email, password):
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = email
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
    else:
        st.success(f"Signed in as: {st.session_state['user_email']}")
        st.markdown("")
        if st.button("Log out", key="logout_btn"):
            st.session_state['logged_in'] = False
            st.session_state['user_email'] = None
            st.experimental_rerun()

if not st.session_state['logged_in']:
    st.info("Please sign in or create an account from the left sidebar to use the predictor and view your history.")
    st.stop()

# --- Prediction UI (requires login) ---
st.subheader('Predict SMS')

# Initialize clear flag in session state
if 'clear_sms' not in st.session_state:
    st.session_state['clear_sms'] = False

col1, col2 = st.columns([4, 1])
with col1:
    input_sms = st.text_area("Enter SMS to classify", height=120, value="" if st.session_state['clear_sms'] else None, key="sms_input_area")
with col2:
    st.markdown("")
    st.markdown("")
    if st.button('🔄 Clear', key="clear_btn", help="Clear the SMS input"):
        st.session_state['clear_sms'] = True
        st.experimental_rerun()

# Reset the clear flag after rerun
if st.session_state['clear_sms']:
    st.session_state['clear_sms'] = False

if st.button('Predict'):
    if not input_sms or input_sms.strip() == "":
        st.warning("Please enter an SMS message to classify.")
    else:
        steps = transform_text(input_sms)
        if isinstance(steps, dict) and 'transformed' in steps:
            transformed_sms = steps['transformed']
        else:
            transformed_sms = steps if isinstance(steps, str) else str(steps)
            steps = {'transformed': transformed_sms}
        
        vector_input = tk.transform([transformed_sms])
        result = model.predict(vector_input)[0]
        label = 'spam' if int(result) == 1 else 'not_spam'
        
        if int(result) == 1:
            st.error('Prediction: SPAM')
        else:
            st.success('Prediction: HAM (not spam)')
        
        # Show decoding steps
        with st.expander('Show decoding steps'):
            if isinstance(steps, dict):
                for key, value in steps.items():
                    st.write(f"**{key}**: {value}")
            else:
                st.write(steps)
        
        try:
            save_prediction(
                st.session_state['user_email'],
                input_sms,
                transformed_sms,
                steps,
                int(result),
                label
            )
            st.success('Prediction saved to your history')
        except Exception as e:
            st.error(f'Failed to save prediction to DB: {e}')

# --- User History ---
st.subheader('Your History')
if st.session_state.get('logged_in') and st.session_state.get('user_email'):
    try:
        items = get_user_predictions(st.session_state['user_email'], limit=50)
        if not items:
            st.info('No prediction history found for your account.')
        else:
            # Create table data
            table_data = []
            for it in items:
                table_data.append({
                    'SMS Text': it.get('text', '')[:100],  # Truncate long text
                    'Prediction': it.get('label', 'n/a').upper(),
                    'Date & Time': str(it.get('timestamp', ''))
                })
            
            # Display as table
            import pandas as pd
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f'Failed to load history: {e}')
else:
    st.info('Please log in to view your prediction history.')
