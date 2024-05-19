from aiogram import Router, types, F
from defaults import *
from utils import is_completed_quest

result_router = Router()


@result_router.message(F.text == '🏅Ачивкалар🏅')
async def get_results(message: types.Message):
    if is_completed_quest(message.from_user.id):
        return await message.answer(responses.get("user_results")[1])
    await message.answer(responses.get("user_results")[0])