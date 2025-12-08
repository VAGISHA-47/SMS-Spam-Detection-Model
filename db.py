from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "sms_spam_db")

# Create a global client so connection is reused by the app
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]


def get_db():
    """Return the MongoDB database object."""
    return db

# --- User Auth Helpers ---
import bcrypt
from datetime import datetime

def create_user(email, password):
    users = db['users']
    if not email or not password:
        return False, "Email and password required."
    if users.find_one({'email': email}):
        return False, "User already exists."
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    users.insert_one({
        'email': email,
        'password_hash': hashed,
        'created_at': datetime.utcnow()
    })
    return True, "User created."

def authenticate_user(email, password):
    users = db['users']
    user = users.find_one({'email': email})
    if not user:
        return False
    hashed = user.get('password_hash')
    if not hashed:
        return False
    return bcrypt.checkpw(password.encode(), hashed)
