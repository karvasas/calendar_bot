from datetime import datetime, timezone, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from database.requests import get_user_data, save_user_credentials
from services.google_calendar import get_calendar_service
from services.scheduler import format_event_date

router = Router()

def get_week_bounds(next_week=False):
    now_utc = datetime.now(timezone.utc)
    current_weekday = now_utc.weekday()
    start_of_current_week = (now_utc - timedelta(days=current_weekday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    if next_week:
        start = start_of_current_week + timedelta(days=7)
    else:
        start = start_of_current_week
    end = start + timedelta(days=7)
    return start.isoformat(), end.isoformat()

async def get_and_send_week_events(message: types.Message, title_prefix: str, next_week: bool):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    if not user_data or not user_data[0]:
        await message.answer("⚠️ авторизуйтесь через /start")
        return

    await message.answer(f"📅 загружаю расписание на {title_prefix}...")

    try:
        service, updated_creds = get_calendar_service(user_data[0])
        save_user_credentials(user_id, updated_creds.to_json()) # сохр. токен
        
        time_min, time_max = get_week_bounds(next_week=next_week)
        events_result = service.events().list(
            calendarId='primary', timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            await message.answer(f"📭 пусто.")
            return
            
        response_text = f"<b>📅 Встречи на {title_prefix}:</b>\n\n"
        for idx, event in enumerate(events, 1):
            title = event.get('summary', 'Без названия')
            start_dict = event.get('start', {})
            end_dict = event.get('end', {})
            
            if 'dateTime' in start_dict:
                start_time = datetime.fromisoformat(start_dict['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end_dict['dateTime'].replace('Z', '+00:00'))
            else:
                start_time = datetime.fromisoformat(start_dict['date']).replace(tzinfo=timezone.utc)
                end_time = datetime.fromisoformat(end_dict['date']).replace(tzinfo=timezone.utc)
                
            formatted_time = format_event_date(start_time, end_time)
            response_text += f"{idx}. <b>{title}</b>\n⏰ {formatted_time}\n\n"
            
        await message.answer(response_text)
    except Exception:
        await message.answer("❌ ошибка api.")

@router.message(Command("week"))
async def cmd_week(message: types.Message):
    await get_and_send_week_events(message, "эту неделю", next_week=False)

@router.message(Command("next_week"))
async def cmd_next_week(message: types.Message):
    await get_and_send_week_events(message, "следующую неделю", next_week=True)