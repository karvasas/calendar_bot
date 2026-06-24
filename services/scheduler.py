import logging
from datetime import datetime, timezone, timedelta
from aiogram import Bot
from database.requests import get_all_users, is_reminder_sent, mark_reminder_as_sent, save_user_credentials
from services.google_calendar import get_calendar_service

months_ru = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def format_event_date(start_dt: datetime, end_dt: datetime) -> str:
    msk_tz = timezone(timedelta(hours=3))
    start_msk = start_dt.astimezone(msk_tz)
    end_msk = end_dt.astimezone(msk_tz)
    time_range = f"{start_msk.strftime('%H:%M')}-{end_msk.strftime('%H:%M')}"
    return f"{start_msk.day} {months_ru[start_msk.month]} {start_msk.year}, {time_range} (МСК)"

async def check_calendar_updates(bot: Bot):
    # фоновая рассылка уведомлений
    users = get_all_users()
    now_utc = datetime.now(timezone.utc)

    for user_id, creds_json, remind_minutes in users:
        try:
            service, updated_creds = get_calendar_service(creds_json)
            save_user_credentials(user_id, updated_creds.to_json())
            
            time_min = now_utc.isoformat()
            time_max = (now_utc + timedelta(hours=3)).isoformat()
            
            events_result = service.events().list(
                calendarId='primary', timeMin=time_min, timeMax=time_max,
                singleEvents=True, orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            for event in events:
                event_id = event['id']
                start_dict = event.get('start', {})
                end_dict = event.get('end', {})
                
                if not start_dict:
                    continue
                
                # защита от событий на весь день
                if 'dateTime' in start_dict:
                    start_time = datetime.fromisoformat(start_dict['dateTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
                    end_time = datetime.fromisoformat(end_dict['dateTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
                else:
                    start_time = datetime.fromisoformat(start_dict['date']).replace(tzinfo=timezone.utc)
                    end_time = datetime.fromisoformat(end_dict['date']).replace(tzinfo=timezone.utc)
                
                if not is_reminder_sent(user_id, event_id):
                    time_delta = start_time - now_utc
                    target_delta = timedelta(minutes=remind_minutes)
                    
                    if timedelta(0) <= time_delta <= target_delta:
                        title = event.get('summary', 'Без названия')
                        link = event.get('htmlLink', 'Ссылка отсутствует')
                        formatted_time = format_event_date(start_time, end_time)
                        
                        msg_text = (
                            f"⏰ <b>Напоминание!</b>\n"
                            f"Встреча: \"{title}\"\n"
                            f"Время: {formatted_time}\n"
                            f"Ссылка: {link}"
                        )
                        await bot.send_message(chat_id=user_id, text=msg_text)
                        mark_reminder_as_sent(user_id, event_id)

        except Exception as e:
            logging.error(f"ошибка планировщика: {e}")