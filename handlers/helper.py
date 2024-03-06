from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from message import *

helper_router = Router()


@helper_router.message(Command('help'))
async def command_help_handler(message: types.Message):
    await message.answer(HELP_COMMAND)


@helper_router.message(lambda message: message.text.lower() == '🙏помощь🙏')
async def get_results(message: types.Message):
    await message.answer(HELP_COMMAND)
