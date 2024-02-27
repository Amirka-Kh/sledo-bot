import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

from message import *
from config import settings
from kbs import *
import models
from handlers import feedback, quest
from database import SessionLocal, engine

bot = Bot(settings.token_api)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.user_tg_id == message.from_user.id).first()
    # Add new user if it doesn't exist
    if not user:
        try:
            new_user = models.User(
                user_tg_id=message.from_user.id,
                username=message.from_user.username,
                name=message.from_user.first_name,
                surname=message.from_user.last_name
            )
            db.add(new_user)
            db.commit()
        finally:
            db.close()
    await message.answer(text=BOT_DESC, parse_mode='HTML', reply_markup=kb_client)


@dp.message(Command('help'))
async def command_help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, text=HELP_COMMAND)


@dp.message(lambda message: message.text.lower() == '🙏помощь🙏')
async def get_help(message: types.Message):
    await command_help_handler(message)


async def main() -> None:
    # await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(feedback.router)
    dp.include_router(quest.quest_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    models.Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
