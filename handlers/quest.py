import asyncio

from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import Levenshtein

from message import *
import models
from database import SessionLocal
from main import bot


quest_router = Router()


@quest_router.message(lambda message: message.text.lower() == '🧩квесты🧩')
async def show_quests(message: types.Message):
    available_quests = get_available_quests(message.from_user.id)

    if not available_quests:
        await message.answer_sticker('CAACAgIAAxkBAAELngRl6BRy2OmPCcArsg6NV2_9FGuwJQACBAEAAladvQreBNF6Zmb3bDQE')
        return await message.answer(responses.get('no_quests'))

    inline_keyboard = []
    for quest in available_quests:
        inline_keyboard.append([InlineKeyboardButton(text=quest, callback_data=f"quest_{quest}")])
    quest_options = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.answer_sticker('CAACAgIAAxkBAAELk8Jl4GF1ScqCo96ktBBW8xKzgjNToAACSQIAAladvQoqlwydCFMhDjQE')
    await message.answer(responses.get('quests'), reply_markup=quest_options)


def get_available_quests(user_id):
    available_quests = []
    for quest in quests:
        if is_quest_finished(user_id, quest):
            continue
        if is_quest_free_to_user(user_id, quest):
            available_quests.append(quest)
    return available_quests


def is_quest_finished(user_id, quest_name):
    quest = get_quest_by_name(user_id, quest_name)
    if quest:
        return quest.finished
    return False


def is_quest_free_to_user(user_id, quest_name):
    if not quests.get(quest_name).get('free'):
        user = get_user(user_id)
        if user:
            return user.paid
        return False
    return True


@quest_router.callback_query(lambda query: query.data.startswith('quest'))
async def process_quest(callback_query: types.CallbackQuery):
    quest_name = callback_query.data.split('_')[1]
    await bot.answer_callback_query(callback_query.id)
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Назад ❌', callback_data=f"start_back_nothing"),
            InlineKeyboardButton(text='Начать ✅', callback_data="start_start_{}".format(quest_name)),
        ]
    ])
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=quests.get(quest_name).get('description'),
                                reply_markup=inline_keyboard)


@quest_router.callback_query(lambda query: query.data.startswith('start'))
async def process_start(callback_query: types.CallbackQuery):
    option = callback_query.data.split('_')[1]
    quest_name = callback_query.data.split('_')[2]
    user_id = callback_query.from_user.id
    if option == 'start':
        await add_quest(user_id, quest_name)
        await bot.answer_callback_query(callback_query.id)
        await send_quest_step(user_id)
    elif option == 'back':
        await bot.answer_callback_query(callback_query.id)
        message = callback_query.message
        available_quests = get_available_quests(message.from_user.id)
        if not available_quests:
            return await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                               message_id=callback_query.message.message_id,
                                               text=responses.get('no_quests'))
        inline_keyboard = []
        for quest in available_quests:
            inline_keyboard.append([InlineKeyboardButton(text=quest, callback_data=f"quest_{quest}")])
        quest_options = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                           message_id=callback_query.message.message_id,
                                           text=responses.get('quests'),
                                           reply_markup=quest_options)


async def add_quest(user_id, quest_name):
    db = SessionLocal()
    try:
        quest_query = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.active == True)
        quest_query.update({"active": False}, synchronize_session=False)
        db.commit()
        # Add new quest if not exists
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.quest_name == quest_name).first()
        if not quest:
            new_quest = models.Quest(player_id=user_id, quest_name=quest_name, active=True)
            db.add(new_quest)
            db.commit()
        else:
            quest_query = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.quest_name == quest_name)
            quest_query.update({"active": True}, synchronize_session=False)
            db.commit()
    finally:
        db.close()


async def send_quest_step(user_id):
    quest = get_quest(user_id)
    step, quest_name = quest.step, quest.quest_name
    riddles = quests.get(quest_name).get('puzzles')
    if step < len(riddles):
        riddle = riddles[step]
        answer_keyboard = []
        for answer in riddle['options']:
            answer_keyboard.append([InlineKeyboardButton(text=answer, callback_data=f"answer_{answer}")])
        answer_options = InlineKeyboardMarkup(inline_keyboard=answer_keyboard)
        if riddle['image']:
            return await bot.send_photo(user_id, riddle['image'],
                                        caption=riddle['description'], reply_markup=answer_options)
        await bot.send_message(user_id, riddle['description'], reply_markup=answer_options)
    else:
        await update_quest(user_id, {"active": False, "finished": True})
        if quests.get(quest_name).get('offer', None):
            if quests.get(quest_name).get('offer_image'):
                return await bot.send_photo(user_id, quests.get(quest_name).get('offer_image'),
                                            caption=quests.get(quest_name).get('offer'))
            return await bot.send_message(user_id, quests.get(quest_name).get('offer'))
        await bot.send_message(user_id, responses.get('congratulation'))
        await asyncio.sleep(2)
        return await bot.send_message(user_id, responses.get('so_whats_next'))


@quest_router.callback_query(lambda query: query.data.startswith('answer'))
async def process_answer(callback_query: types.CallbackQuery):
    option = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    quest = get_quest(user_id)
    if quest:
        riddles = quests.get(quest.quest_name).get('puzzles')
        step = quest.step
        riddle = riddles[step]

        distance = Levenshtein.distance(option, riddle['answer'])
        if distance < 4:    # less than threshold
            await bot.send_message(user_id, riddle['wait'])
            await update_quest(user_id, {"step": step + 1})
            await asyncio.sleep(2)
            await send_quest_step(user_id)
        else:
            await bot.send_message(user_id, riddle['wait'])
            await asyncio.sleep(2)
            await bot.send_message(user_id, riddle['exception'].format(answer=option))
    else:
        await bot.send_message(user_id, responses.get('db_problem'))


def get_user(user_id):
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.user_tg_id == user_id).first()
        return user
    finally:
        db.close()


def get_quest(user_id):
    db = SessionLocal()
    try:
        quest = db.query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.active == True).first()
        return quest
    finally:
        db.close()


def get_quest_by_name(user_id, quest_name):
    db = SessionLocal()
    try:
        quest = db .query(models.Quest).filter(models.Quest.player_id == user_id, models.Quest.quest_name == quest_name).first()
        return quest
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


@quest_router.message(lambda message: message.text.lower() != '👽👂👣👹🔥☠️')
async def check_answer(message: types.Message):
    # Checking the answer
    user_id = message.from_user.id
    quest = get_quest(user_id)
    if quest:
        riddles = quests.get(quest.quest_name).get('puzzles')
        step = quest.step
        riddle = riddles[step]

        distance = Levenshtein.distance(message.text.lower(), riddle['answer'])
        if distance < 4:  # less than threshold
            await bot.send_message(user_id, riddle['wait'])
            await update_quest(user_id, {"step": step + 1})
            await asyncio.sleep(2)
            await send_quest_step(user_id)
        else:
            await bot.send_message(user_id, riddle['wait'])
            await asyncio.sleep(2)
            await bot.send_message(user_id, riddle['exception'].format(answer=message.text.lower()))
    else:
        await bot.send_message(user_id, responses.get('db_problem'))
