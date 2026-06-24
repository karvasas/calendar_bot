import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database.connection import init_db
from handlers import start, reminders, history, status, week
from services.scheduler import check_calendar_updates

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def main():
    init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        status.router,
        week.router,
        history.router,
        reminders.router
    )

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_calendar_updates, "interval", minutes=5, args=[bot])
    scheduler.start()

    logging.info("Бот запущен.")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())