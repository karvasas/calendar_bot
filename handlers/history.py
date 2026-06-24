from datetime import datetime, timezone, timedelta
from aiogram import Router, types
from aiogram.filters import Command
from database.requests import get_user_data, get_user_history, save_to_history, save_user_credentials
from services.google_calendar import get_calendar_service

router = Router()

@router.message(Command("history"))
async def cmd_history(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data or not user_data[0]:
        await message.answer("⚠️ авторизуйтесь через /start")
        return

    try:
        service, updated_creds = get_calendar_service(user_data[0])
        save_user_credentials(user_id, updated_creds.to_json()) # сохр. токен
        
        now_utc = datetime.now(timezone.utc)
        time_min = (now_utc - timedelta(days=30)).isoformat()
        time_max = now_utc.isoformat()
        
        events_result = service.events().list(
            calendarId='primary', timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        for event in events:
            start_dict = event.get('start', {})
            end_dict = event.get('end', {})
            if not start_dict:
                continue
                
            if 'dateTime' in start_dict:
                start_time = datetime.fromisoformat(start_dict['dateTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
                end_time = datetime.fromisoformat(end_dict['dateTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
            else:
                start_time = datetime.fromisoformat(start_dict['date']).replace(tzinfo=timezone.utc)
                end_time = datetime.fromisoformat(end_dict['date']).replace(tzinfo=timezone.utc)
            
            if end_time < now_utc:
                title = event.get('summary', 'Без названия')
                msk_tz = timezone(timedelta(hours=3))
                start_msk = start_time.astimezone(msk_tz)
                end_msk = end_time.astimezone(msk_tz)
                hist_time = f"{start_msk.strftime('%d.%m.%Y %H:%M')}-{end_msk.strftime('%H:%M')}"
                
                current_history = [h[1] for h in get_user_history(user_id)]
                if title not in current_history:
                    save_to_history(user_id, title, hist_time)
    except Exception:
        pass

    history_data = get_user_history(user_id)
    if not history_data:
        await message.answer("📭 история пуста.")
        return

    response_text = "<b>Последние 10 встреч:</b>\n"
    for idx, (event_time, title) in enumerate(history_data, 1):
        response_text += f"{idx}. [{event_time}] {title}\n"
        
    await message.answer(response_text)