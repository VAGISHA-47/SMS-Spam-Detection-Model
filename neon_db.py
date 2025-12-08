import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()

NEON_DB_URL = os.getenv("NEON_DB_URL", "")

def get_connection():
    """Get a connection to Neon DB."""
    if not NEON_DB_URL:
        raise ValueError("NEON_DB_URL not set in environment variables")
    return psycopg2.connect(NEON_DB_URL)

def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create predictions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
            user_email VARCHAR(255) NOT NULL,
            text TEXT NOT NULL,
            transformed TEXT,
            steps JSON,
            prediction INT,
            label VARCHAR(50),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def create_user(email, password):
    """Create a new user with hashed password."""
    email = email.strip().lower() if email else ""
    password = password.strip() if password else ""
    
    if not email or not password:
        return False, "Email and password required."
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "User already exists."
        
        # Hash password and insert user
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, hashed)
        )
        conn.commit()
        return True, "User created."
    except Exception as e:
        return False, f"Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()

def authenticate_user(email, password):
    """Authenticate user by email and password."""
    email = email.strip().lower() if email else ""
    password = password.strip() if password else ""
    
    if not email or not password:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return False
        
        hashed_str = row[0]
        # Convert to bytes if needed
        if isinstance(hashed_str, str):
            hashed_bytes = hashed_str.encode('utf-8')
        else:
            hashed_bytes = hashed_str
        
        return bcrypt.checkpw(password.encode('utf-8'), hashed_bytes)
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def save_prediction(user_email, text, transformed, steps, prediction, label):
    """Save a prediction to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        import json
        steps_json = json.dumps(steps) if isinstance(steps, dict) else steps
        cursor.execute(
            """INSERT INTO predictions 
               (user_email, text, transformed, steps, prediction, label) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_email, text, transformed, steps_json, prediction, label)
        )
        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_predictions(user_email, limit=50):
    """Get all predictions for a user."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """SELECT id, text, transformed, steps, prediction, label, timestamp 
               FROM predictions 
               WHERE user_email = %s 
               ORDER BY timestamp DESC 
               LIMIT %s""",
            (user_email, limit)
        )
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        cursor.close()
        conn.close()
