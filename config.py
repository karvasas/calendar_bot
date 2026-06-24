import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = "database.db"
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

if not BOT_TOKEN:
    raise ValueError("переменная BOT_TOKEN не найдена")