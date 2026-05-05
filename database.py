import sqlite3
import pickle
import datetime

DB_NAME = "iris_auth.db"

def get_conn():
    """Returns a database connection with WAL mode and timeout to prevent locking."""
    conn = sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)
    # WAL mode allows multiple readers + one writer simultaneously
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def init_db():
    """Initializes the database with users and logs tables."""
    conn = get_conn()
    cursor = conn.cursor()
    # Users table stores the username and serialized ORB features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            features BLOB NOT NULL
        )
    ''')
    # Logs table stores login attempts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, features):
    """Registers a new user into the database."""
    try:
        conn = get_conn()
        cursor = conn.cursor()
        # Serialize the numpy features using pickle
        features_blob = pickle.dumps(features)
        cursor.execute("INSERT INTO users (username, features) VALUES (?, ?)", (username, features_blob))
        conn.commit()
        conn.close()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, str(e)

def get_users():
    """Retrieves all users and their features from the database."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username, features FROM users")
    rows = cursor.fetchall()
    conn.close()

    users_data = {}
    for row in rows:
        username = row[0]
        # Deserialize the features
        features = pickle.loads(row[1])
        users_data[username] = features
    return users_data

def delete_user(username):
    """Deletes a user from the database."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def log_attempt(username, status):
    """Logs an authentication attempt."""
    conn = get_conn()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (username, timestamp, status) VALUES (?, ?, ?)", (username, timestamp, status))
    conn.commit()
    conn.close()

def get_logs():
    """Retrieves all authentication logs."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT username, timestamp, status FROM logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
