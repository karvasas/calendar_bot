import sqlite3
from config import DB_NAME

def save_user_credentials(user_id: int, creds_json: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, credentials) 
        VALUES (?, ?) 
        ON CONFLICT(user_id) DO UPDATE SET credentials = excluded.credentials
    """, (user_id, creds_json))
    conn.commit()
    conn.close()

def get_user_data(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT credentials, remind_minutes FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, credentials, remind_minutes FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_user_reminder(user_id: int, minutes: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET remind_minutes = ? WHERE user_id = ?", (minutes, user_id))
    conn.commit()
    conn.close()

def save_to_history(user_id: int, title: str, event_time: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history (user_id, title, event_time) VALUES (?, ?, ?)", (user_id, title, event_time))
    conn.commit()
    conn.close()

def get_user_history(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT event_time, title FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 10", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def is_reminder_sent(user_id: int, event_id: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_reminders WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_reminder_as_sent(user_id: int, event_id: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO sent_reminders (user_id, event_id) VALUES (?, ?)", (user_id, event_id))
    conn.commit()
    conn.close()