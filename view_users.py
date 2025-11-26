import sqlite3
import json
import os

DB_NAME = "users.db"

DB_PATH = os.path.abspath(DB_NAME)
print(f"Database path: {DB_PATH}")
user_id = 6  # change this to the ID you want to delete

def view_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, email, token_json FROM users")
    rows = cursor.fetchall()
    
    if not rows:
        print("No users found in the database.")
        conn.close()
        return
    
    print("=" * 80)
    print("USERS IN DATABASE")
    print("=" * 80)
    print()
    
    for row in rows:
        user_id, email, token_json = row
        print(f"ID: {user_id}")
        print(f"Email: {email}")
        
        # Parse token JSON to show some details
        try:
            token_data = json.loads(token_json)
            print(f"Token Type: {token_data.get('token_uri', 'N/A')}")
            print(f"Has Refresh Token: {'Yes' if token_data.get('refresh_token') else 'No'}")
            print(f"Scopes: {', '.join(token_data.get('scopes', []))}")
            print(f"Token Preview: {token_json[:100]}...")
        except:
            print(f"Token JSON: {token_json[:100]}...")
        
        print("-" * 80)
        print()
    
    print(f"Total users: {len(rows)}")
    conn.close()
    
def delete_user(user_id):

    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"User with ID {user_id} deleted.")


if __name__ == "__main__":
    # view_users()
    delete_user(user_id)

