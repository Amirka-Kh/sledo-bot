from aiogram import Router, types
from message import *

result_router = Router()


@result_router.message(lambda message: message.text.lower() == '🏅результаты🏅')
async def get_results(message: types.Message):
    await message.answer(responses.get("user_results"))