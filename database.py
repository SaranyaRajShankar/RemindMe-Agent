import sqlite3
import json

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            token_json TEXT
        )
    """)
    conn.commit()
    conn.close()
    
# Initialize database on import
init_db()

def save_user_token(email, creds):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users (email, token_json)
        VALUES (?, ?)
    """, (email, creds.to_json()))

    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT email, token_json FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_token(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT token_json FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        from google.oauth2.credentials import Credentials
        return Credentials.from_authorized_user_info(json.loads(row[0]))

    return None
