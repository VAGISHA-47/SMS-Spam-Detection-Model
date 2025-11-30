import os
import pymongo
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
client = pymongo.MongoClient(MONGO_URI)
db = client.get_database('sms_spam_app')
users_col = db.get_collection('users')
history_col = db.get_collection('history')

# Detect DB availability
DB_CONNECTED = True
try:
    client.admin.command('ping')
except Exception:
    DB_CONNECTED = False
    # ensure in-memory fallbacks
    if 'local_users' not in st.session_state:
        st.session_state['local_users'] = {}
    if 'local_history' not in st.session_state:
        st.session_state['local_history'] = []


def create_user(username: str, password: str) -> bool:
    if DB_CONNECTED:
        try:
            if users_col.find_one({'username': username}):
                return False
            password_hash = generate_password_hash(password)
            users_col.insert_one({'username': username, 'password_hash': password_hash, 'created_at': datetime.utcnow()})
            return True
        except Exception:
            pass

    local = st.session_state.setdefault('local_users', {})
    if username in local:
        return False
    local[username] = generate_password_hash(password)
    return True


def authenticate(username: str, password: str) -> bool:
    if DB_CONNECTED:
        try:
            user = users_col.find_one({'username': username})
            if user:
                return check_password_hash(user['password_hash'], password)
        except Exception:
            pass

    local = st.session_state.setdefault('local_users', {})
    pw_hash = local.get(username)
    if not pw_hash:
        return False
    return check_password_hash(pw_hash, password)


def save_history(username: str, message: str, label: str):
    if DB_CONNECTED:
        try:
            history_col.insert_one({'username': username, 'message': message, 'label': label, 'timestamp': datetime.utcnow()})
            return
        except Exception:
            pass

    st.session_state.setdefault('local_history', []).append({'username': username, 'message': message, 'label': label, 'timestamp': datetime.utcnow()})


def get_history(username: str, limit: int = 200):
    if DB_CONNECTED:
        try:
            cursor = history_col.find({'username': username}).sort('timestamp', pymongo.DESCENDING).limit(limit)
            return list(cursor)
        except Exception:
            pass

    hist = st.session_state.setdefault('local_history', [])
    filtered = [h for h in hist if h.get('username') == username]
    return sorted(filtered, key=lambda x: x.get('timestamp'), reverse=True)[:limit]
