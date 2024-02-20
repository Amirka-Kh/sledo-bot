import asyncio
import copy
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

import logging
import sys

from config import *

bot = Bot(TOKEN_API)

dp = Dispatcher()

quests_description = {
    "Сладкая Контрабанда": {
        "description": "Добро пожаловать в маленький город, где каждый уголок скрывает свои секреты. Детектив Артур Мэйсон обращается к вам за помощью в расследовании серии загадочных краж, связанных с контрабандой опасно вкусного продукта. Ваша задача - помочь ему найти контрабандистов и раскрыть их тайны.",
        "offer": "Вы поделали хорошую работу, ..."
    }
}

quests = {
    "Сладкая Контрабанда": [
        {"image": "https://img.tourister.ru/files/2/3/1/9/0/6/4/6/clones/870_653_fixedwidth.jpg",
         "description": "Первый раз подозреваемый был замечен возле фонтана четырех жаб. Мы полагаем, что в этот день он остановился неподалеку. Очевидцы говорят, что на этаже, в котором он остановился было 7 окон. Помогите нам узнать название места его остановки (магазин, кафе)",
         "answer": "вернисаж ремесел",
         "exception": "По вашей наводке наши сыщики обыскали {answer}, однако никаких улик не нашли, попробуйте другие варианты"},
        {"image": None,
         "description": "МЫ НАШЛИ ЗАПИСКУ!!! В записке сказано: 'встретимся на перекрестке на точке до Москвы 722 км'. Обследуйте это место и доложите, что вы нашли",
         "answer": "камень",
         "exception": "Эгхх, это точно нам поможет, посмотрите может там есть еще зацепки"},
        {"image": "https://tur-kazan.ru/web/uploads/5c20c05e7cbab.jpg",
         "description": "Отлично! Мы расшивровали послание, подозреваемый сказал, что товар можно будет забрать ночью в упряжке Екатерины 2. Что он имел ввиду? Если у тебя получилось что-то найти, доложи нам скорей",
         "answer": "добрая столовая",
         "exception": "Хмм. Это интересно, однако этого не достаточно, чтобы выйти на преступника. Посмотри, может ты еще что-то найдешь"},
    ],
    "Тайна Пропавшего Шоколада": [
        {"image": None,
         "description": "Утром наша служба безопасности обнаружила, что известный шоколатье, мистер Густав, обвиняет вора в краже его нового рецепта шоколада 'Провансаль'. Подозреваемый был замечен возле улицы 'Шоколадной Галереи'. Посмотрите вокруг и сообщите, если что-то обнаружите.",
         "answer": "записка",
         "exception": "Мы проверили вашу улику, но к сожалению, ничего не нашли. Попробуйте еще раз."},
        {"image": None,
         "description": "Это хорошая улика, наши следователи пробили это имя и подозреваемого. Подозреваемый упоминул, что видел своего партнера неподалеку от магазина 'Шоколадные Изыски'. Посетите это место и сообщите нам о результатах.",
         "answer": "бумага",
         "exception": "Ваши усилия помогли, но нам нужно еще больше информации."},
        {"image": None,
         "description": "Отлично! Мы нашли странный листок бумаги возле магазина 'Шоколадные Изыски'. Он содержит загадочный код: '7-15-20-5-18-2-15-12'. Пожалуйста, попробуйте разгадать его и дайте нам знать результат.",
         "answer": "шоколадница",
         "exception": "Нет! Ваша информация была полезной, но нам нужно еще больше, чтобы поймать преступника."},
    ]
}

user_progress = {}


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    #TODO safe user
    # if message.chat.id not in STATE:
    #     new_chat_state = copy.deepcopy(chat_scheme)
    #     # adapter to safe user with name, surname
    #     new_chat_state['people'].append(message.from_user.username)
    #     STATE[message.chat.id] = new_chat_state
    inline_keyboard = []
    for quest in quests:
        inline_keyboard.append(InlineKeyboardButton(text=quest, callback_data=f"quest_{quest}"))
    quest_options = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])
    await message.answer(text=BOT_DESC, parse_mode='HTML')
    await message.answer("У нас есть следующие активные квесты:", reply_markup=quest_options)


@dp.callback_query(lambda query: query.data.startswith('quest'))
async def process_quest(callback_query: types.CallbackQuery):
    quest_name = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    user_progress[user_id] = {'quest': quest_name, 'step': 0}
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, quests_description.get(quest_name).get('description'))
    # await bot.send_message(user_id, f"Вы выбрали квест {quest_name}. Давайте начнем! Отправьте 'начать'.")
    await send_quest_step(user_id)

async def send_quest_step(user_id):
    progress = user_progress.get(user_id)
    if progress:
        quest_name = progress['quest']
        step = progress['step']
        riddles = quests.get(quest_name)
        if step < len(riddles):
            riddle = riddles[step]
            if riddle['image']:
                await bot.send_photo(user_id, riddle['image'])
            await bot.send_message(user_id, riddle['description'])
        else:
            if not quests_description.get(quest_name).get('offer', None):
                await bot.send_message(user_id, quests_description.get(quest_name).get('offer'))
            else:
                await bot.send_message(user_id, "Поздравляем, вы прошли квест!")
    else:
        await bot.send_message(user_id, "Сначала выберите квест командой /start.")


@dp.message(lambda message: message.text.lower() == 'начать')
async def start_quest(message: types.Message):
    # Starting the quest
    user_id = message.from_user.id
    await send_quest_step(user_id)


@dp.message()
async def check_answer(message: types.Message):
    # Checking the answer
    user_id = message.from_user.id
    progress = user_progress.get(user_id)
    if progress and message.text:
        quest_name = progress['quest']
        step = progress['step']
        riddles = quests.get(quest_name)
        if step < len(riddles):
            riddle = riddles[step]
            #TODO compare leivenstain distance
            if message.text.lower() == riddle['answer']:
                progress['step'] += 1
                await send_quest_step(user_id)
            else:
                await bot.send_message(user_id, riddle['exception'].format(answer=riddle['answer']))
        else:
            await bot.send_message(user_id, "Вы уже прошли все загадки этого квеста.")
    else:
        await bot.send_message(user_id, "Сначала начните квест командой /start.")


@dp.message(F.text == '/help')
async def command_help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, text=HELP_COMMAND)
    await message.delete()


@dp.message(F.text == '/give')
async def command_sticker_getter(message: types.Message):
    await bot.send_sticker(message.from_user.id, sticker="CAACAgIAAxkBAAELPv5lsm2w9MAbdBF4luE65X0ryDgWuAACRyEAAmOvOUjsoVCVkQTwUjQE")


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
