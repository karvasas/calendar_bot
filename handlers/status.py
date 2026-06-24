from aiogram import Router, types
from aiogram.filters import Command
from database.requests import get_user_data
from services.google_calendar import get_calendar_service

router = Router()

@router.message(Command("status"))
async def cmd_status(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    if not user_data or not user_data[0]:
        await message.answer("❌ вы не вошли в аккаунт. введите /start.")
        return
        
    try:
        service, _ = get_calendar_service(user_data[0])
        service.calendarList().list(maxResults=1).execute()
        await message.answer("✅ вы успешно авторизованы! бот видит ваш календарь.")
    except Exception:
        await message.answer("❌ сессия устарела. введите /start заново.")