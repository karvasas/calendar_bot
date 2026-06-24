import sqlite3
from config import DB_NAME

def init_db():
    # инициализация таблиц
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            credentials TEXT,
            remind_minutes INTEGER DEFAULT 15
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            event_time TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_reminders (
            user_id INTEGER,
            event_id TEXT,
            PRIMARY KEY (user_id, event_id)
        )
    """)
    
    conn.commit()
    conn.close()