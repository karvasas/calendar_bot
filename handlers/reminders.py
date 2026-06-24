from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from database.requests import get_user_data, update_user_reminder

router = Router()

@router.message(Command("set_reminder"))
async def cmd_set_reminder(message: types.Message, command: CommandObject):
    user_id = message.from_user.id
    
    if not get_user_data(user_id):
        await message.answer("⚠️ сначала авторизуйтесь через /start")
        return

    if not command.args or not command.args.isdigit():
        await message.answer("⚠️ формат: /set_reminder <минуты>")
        return

    minutes = int(command.args)
    update_user_reminder(user_id, minutes)
    await message.answer(f"🔔 готово! уведомления за {minutes} мин.")