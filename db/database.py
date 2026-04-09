import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "data", "documents.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    # Ensure data folder exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT,
            thumbnail_path TEXT,
            tags TEXT,
            description TEXT,
            upload_date TEXT,
            lecture_date TEXT,
            total_pages INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS page_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            page_number INTEGER,
            
            timestamp TEXT
            
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                timestamp TEXT
            )
    ''')
    conn.commit()
    print("Database initialized successfully.")
    conn.close()