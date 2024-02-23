import psycopg2
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
from kbs import *

import models
from database import SessionLocal, engine

bot = Bot(TOKEN_API)

dp = Dispatcher()

quests_description = {
    "Сладкая Контрабанда": {
        "description": "🔍 На связи СледоБот. В нашем городе заметно увеличилось количество случаев контрабанды. Обращаюсь к вам за помощью в расследовании происшествия, которое произошло недавно на улице Баумана. Ваша задача - помочь нам выявить контрабанду и раскрыть тайны преступников. 🕵️‍♂️",
        "offer": "Вы поделали хорошую работу, ..."
    },
    "Тайна Шоколада": {
        "description": "🍫 У известного шоколатье, мистера Густава, украли рецепт его нового шоколада 'Провансаль'. Мистер Густав обещал хорошую награду тем, кто найдет преступника. Однако надо торопиться, так как это нужно сделать до того, как рецепт окажется у конкурентов. 🕵️‍♂️🚨",
        "offer": None
    }
}

quests = {
    "Сладкая Контрабанда": [
        {"image": "https://img.tourister.ru/files/2/3/1/9/0/6/4/6/clones/870_653_fixedwidth.jpg",
         "description": "🕵️‍♂️ Спасибо, что взялись за это дело. Теперь перейдем к сути.\n\nНаши информаторы доложили, что в последний раз люди видели подозрительного незнакомца возле фонтана с четырьмя жабами. Мы предполагаем, что это наш подозреваемый. Скорее всего, в этот день он остановился неподалеку. Очевидцы говорят, что на этаже, где он остановился, было 7 окон. Помогите нам узнать, в каком месте он остановился. 🕵️‍♀️",
         "answer": "вернисаж ремесел",
         "exception": "🕵️‍♂️ По вашей наводке наши сыщики обыскали {answer}, однако никаких улик не нашли. Попробуйте другие варианты."},
        {"image": None,
         "description": "🔍 Я отправил информаторов на проверку здания...\n\n📝 МЫ НАШЛИ ЗАПИСКУ!!!\n\nВ записке сказано: 'встретимся на перекрестке на точке до Москвы 722 км'. Что это значит? Найдите это место и доложите, что вы нашли. 🗺️",
         "answer": "камень",
         "exception": "😔 Эгхх, это точно нам поможет. Посмотрите, может, там есть еще зацепки?"},
        {"image": "https://s1.stc.all.kpcdn.net/putevoditel/projectid_379258/images/tild3430-6664-4639-b565-373563356665__edc48dc599feca9c544d.jpg",
         "description": "🕵️‍♂️ Проводим проверку...\n\n🔍 Отлично! Мы расшифровали послание. Подозреваемый сказал, что товар можно будет забрать ночью в упряжке Екатерины II. Эгхх, что? Если у тебя получилось что-то найти, доложи нам скорее. 📦🌙",
         "answer": "добрая столовая",
         "exception": "🤔 Хмм, это интересно, однако этого недостаточно, чтобы выйти на след преступника. Посмотри, может, ты еще что-то найдешь?"},
    ],
    "Тайна Шоколада": [
        {"image": None,
         "description": "🍫 Сегодня тебе предстоит заняться очень странным делом. Утром наша служба безопасности обнаружила, что известный шоколатье, мистер Густав, обвиняет вора в краже его нового рецепта шоколада 'Провансаль'. Подозреваемый был замечен возле улицы 'Шоколадной Галереи'. Посмотрите вокруг и сообщите, если что-то обнаружите. 🕵️‍♂️🔍",
         "answer": "записка",
         "exception": "🔍 Мы проверили твою улику, но к сожалению, ничего не нашли. Попробуй еще раз. 🤔"},
        {"image": None,
         "description": "🕵️‍♂️ Отлично, наши следователи проанализировали записку и расшифровали имя 'Мортез'.\n\n🔍 Мортез, Мортез... Хмм... Проверь магазин 'Шоколадные Изыски'. Хозяина этого ресторана зовут Дартаньян. Может быть, он что-то знает? 🤔🍫",
         "answer": "бумага",
         "exception": "Ваши усилия помогли, но нам нужно еще больше информации. 📝🔍"},
        {"image": None,
         "description": "Теперь, когда мы знаем, кто такой 'Мортез', мы можем его поймать. Наш 'Мортез', или Артём, назначил встречу с директором 'Сладкой Жизни'. Я думаю, ты можешь представиться директором и выведать у него конфиденциальную информацию. Мы надеемся на тебя, больше у нас такого шанса может не быть. 🕵️‍♂️🔍",
         "answer": "шоколадница",
         "exception": "Нет! Ваша информация была полезной, но нам нужно еще больше, чтобы поймать преступника. 🚨🔍"},
    ],
}


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.user_tg_id == message.from_user.id).first()
    # Check if user exists
    if not user:
        try:
            tg_user_id = message.from_user.id
            username = message.from_user.username
            name = message.from_user.first_name
            surname = message.from_user.last_name
            new_user = models.User(user_tg_id=tg_user_id, username=username, name=name, surname=surname)
            db.add(new_user)
            db.commit()
        finally:
            db.close()
    await message.answer(text=BOT_DESC, parse_mode='HTML', reply_markup=kb_client)


@dp.message(lambda message: message.text.lower() == 'квесты')
async def show_quests(message: types.Message):
    inline_keyboard = []
    for quest in quests:
        inline_keyboard.append(InlineKeyboardButton(text=quest, callback_data=f"quest_{quest}"))
    quest_options = InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])
    await message.answer("У нас есть следующие активные квесты 🗺:", reply_markup=quest_options)


def check_quest_status(user_id, quest_name):
    quest = get_quest_by_name(user_id, quest_name)
    if quest:
        step, quest_name = quest.step, quest.quest_name
        riddles = quests.get(quest_name)
        if step == len(riddles):
            return True
    return False


@dp.callback_query(lambda query: query.data.startswith('quest'))
async def process_quest(callback_query: types.CallbackQuery):
    quest_name = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    await bot.answer_callback_query(callback_query.id)
    if check_quest_status(user_id, quest_name):
        return await bot.send_message(user_id, "Квест уже пройдён")
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад ❌', callback_data=f"start_back_nothing"),
            InlineKeyboardButton(text='Начать ✅', callback_data="start_start_{}".format(quest_name)),
        ]
    ])
    await bot.send_message(user_id, quests_description.get(quest_name).get('description'), reply_markup=inline_keyboard)


@dp.callback_query(lambda query: query.data.startswith('start'))
async def process_start(callback_query: types.CallbackQuery):
    option = callback_query.data.split('_')[1]
    quest_name = callback_query.data.split('_')[2]
    user_id = callback_query.from_user.id
    if option == 'start':
        db = SessionLocal()
        try:
            new_quest = models.Quest(player_id=user_id, quest_name=quest_name, active=True)
            db.add(new_quest)
            db.commit()
        finally:
            db.close()
        await bot.answer_callback_query(callback_query.id)
        await send_quest_step(user_id)
    elif option == 'back':
        await bot.answer_callback_query(callback_query.id)
        message = callback_query.message
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


async def send_quest_step(user_id):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.active == True).first()
        step, quest_name = quest.step, quest.quest_name
        riddles = quests.get(quest_name)
        if step < len(riddles):
            riddle = riddles[step]
            if riddle['image']:
                await bot.send_photo(user_id, riddle['image'])
            await bot.send_message(user_id, riddle['description'])
        else:
            await update_quest(user_id, {"active": False})
            if quests_description.get(quest_name).get('offer', None):
                await bot.send_message(user_id, quests_description.get(quest_name).get('offer'))
            else:
                await bot.send_message(user_id, "Поздравляем, вы прошли квест!")
    finally:
        db.close()


@dp.message(lambda message: message.text.lower() == 'помощь')
async def show_help(message: types.Message):
    await command_help_handler(message)


@dp.message(lambda message: message.text.lower() == 'результаты')
async def show_results(message: types.Message):
    await message.answer("Молодец! Спасибо за прохождение квестов 🙏")


@dp.message(lambda message: message.text.lower() == 'feedback')
async def show_results(message: types.Message):
    await message.answer("Спасибо за feedback 🙏")


@dp.message(F.text == '/help')
async def command_help_handler(message: types.Message):
    await bot.send_message(message.from_user.id, text=HELP_COMMAND)


def get_quest_by_name(user_id, quest_name):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.quest_name == quest_name).first()
        if quest:
            return quest
        return None
    finally:
        db.close()

def get_quest(user_id):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.active == True).first()
        if quest:
            return quest
        return None
    finally:
        db.close()


async def update_quest(user_id, data):
    db = SessionLocal()
    try:
        quest_query = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.active == True)
        quest_query.update(data, synchronize_session=False)
        db.commit()
    finally:
        db.close()


@dp.message()
async def check_answer(message: types.Message):
    # Checking the answer
    user_id = message.from_user.id
    quest = get_quest(user_id)
    if quest:
        step, quest_name = quest.step, quest.quest_name
        riddles = quests.get(quest_name)
        if step < len(riddles):
            riddle = riddles[step]
            # TODO compare leivenstain distance
            if message.text.lower() == riddle['answer']:
                await bot.send_message(user_id, "Проверяем...")
                await update_quest(user_id, {"step": step + 1})
                await send_quest_step(user_id)
            else:
                await bot.send_message(user_id, riddle['exception'].format(answer=riddle['answer']))
        else:
            await update_quest(user_id, {"active": False})
            await bot.send_message(user_id, "Вы уже прошли все загадки этого квеста.")
    else:
        await bot.send_message(user_id, "Не удалось найти информацию о вашем текущем квесте.")


@dp.message(F.text == '/give')
async def command_sticker_getter(message: types.Message):
    await bot.send_sticker(message.from_user.id, sticker="CAACAgIAAxkBAAELPv5lsm2w9MAbdBF4luE65X0ryDgWuAACRyEAAmOvOUjsoVCVkQTwUjQE")


async def main() -> None:
    await dp.start_polling(bot)

if __name__ == '__main__':
    models.Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
