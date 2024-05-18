from aiogram import Router, types, F
from aiogram.filters import Command
from defaults import *

helper_router = Router()


@helper_router.message(Command('help'))
async def command_help_handler(message: types.Message):
    await message.answer(HELP_COMMAND)


@helper_router.message(F.text == '🙏Ярдәм🙏')
async def get_results(message: types.Message):
    await message.answer(HELP_COMMAND)
