import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SCOPES
from database.requests import save_user_credentials

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    await message.answer("👋 Привет! Открываю браузер для авторизации в Google Calendar...")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = await asyncio.to_thread(
            flow.run_local_server, port=0, open_browser=True,
            prompt="consent", access_type="offline"
        )
        save_user_credentials(user_id, creds.to_json())
        
        await message.answer(
            "✅ Авторизация успешна!\n\n"
            "Команды:\n/week — планы на неделю\n/next_week — следующая неделя\n"
            "/history — история встреч\n/set_reminder <минуты> — настройка уведомлений"
        )
    except Exception as e:
        await message.answer("❌ Ошибка авторизации. Проверьте консоль.")