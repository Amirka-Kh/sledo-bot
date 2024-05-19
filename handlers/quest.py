import asyncio
import os

from aiogram import types, Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
import Levenshtein

from quests.message import *
from defaults import *
import models
from database import SessionLocal
from main import bot
from services.image_recognition import prepare_model, predict_image

model = prepare_model()
quest_router = Router()


@quest_router.message(F.text == '👽👂👣🔥☠️')
async def say_wait(message: types.Message):
    await message.answer(responses.get('wait'))


@quest_router.message(F.text == '🧩Маҗаралар🧩')
async def show_quests(message: types.Message):
    available_quests = get_available_quests(message.from_user.id)

    if not available_quests:
        await message.answer_sticker('CAACAgIAAxkBAAEMJPVmSQOhWySNZMXqxuRavyVlO6zvjQACeQEAAiteUwulfjaelBVlqzUE')
        return await message.answer(responses.get('no_quests'))

    inline_keyboard = []
    for quest in available_quests:
        inline_keyboard.append([InlineKeyboardButton(text=quest, callback_data=f"quest_{quest}")])
    quest_options = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await message.answer_sticker('CAACAgIAAxkBAAEMJPlmSQPFmFRKWSbfmFr304ZTyqvjGQACaQEAAiteUwuCQO6F5TN9lDUE')
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
            InlineKeyboardButton(text='Кире кайту ❌', callback_data=f"start_back_nothing"),
            InlineKeyboardButton(text='Башлау ✅', callback_data="start_start_{}".format(quest_name)),
        ]
    ])
    # Delete the original text message
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    return await bot.send_photo(
        chat_id=callback_query.message.chat.id,  # Chat ID
        photo=quests.get(quest_name).get('description_image'),  # Image URL or file ID
        caption=quests.get(quest_name).get('description'),  # Caption text
        reply_markup=inline_keyboard  # Inline keyboard markup
    )


@quest_router.callback_query(lambda query: query.data.startswith('again'))
async def process_quest(callback_query: types.CallbackQuery):
    decision = callback_query.data.split('_')[1]
    await bot.answer_callback_query(callback_query.id)
    if decision == 'back':
        return await bot.send_message(callback_query.from_user.id, responses.get('see_you'))
    return await send_quest_step(callback_query.from_user.id)


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
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        return await bot.send_message(message.chat.id, responses.get('quests'), reply_markup=quest_options)
        # return await show_quests(callback_query.message)


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


async def start_again(user_id, step):
    step = abs(step) * 10
    start_again_options = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Икенче тапкыр ❌', callback_data=f"again_back"),
            InlineKeyboardButton(text='Эйдә ✅', callback_data="again_start"),
        ]
    ])
    await update_quest(user_id, {"step": 1})
    return await bot.send_message(user_id, responses['start_again'].format(step), reply_markup=start_again_options)


async def send_quest_step(user_id):
    quest = get_quest(user_id)
    step, quest_name = quest.step, quest.quest_name
    if step > -10 & step <= -1:
        return await start_again(user_id, step)
    if step == -10:
        await update_quest(user_id, {"active": False, "finished": True})
        if quests.get(quest_name).get('offer', None):
            if quests.get(quest_name).get('offer_image'):
                return await bot.send_photo(user_id, quests.get(quest_name).get('offer_image'),
                                            caption=quests.get(quest_name).get('offer'))
            return await bot.send_message(user_id, quests.get(quest_name).get('offer'))
        await bot.send_message(user_id, responses.get('congratulation'))
        await asyncio.sleep(1)
        return await bot.send_message(user_id, responses.get('so_whats_next'))
    riddles = quests.get(quest_name).get('puzzles')
    riddle = riddles[str(step)]
    answer_keyboard = []
    for answer in riddle['options']:
        callback_data = f"answer_{riddle['options'][answer]}"
        # print(f"Callback data: {callback_data}")
        if len(callback_data) > 64:
            callback_data = callback_data[:64]
        # callback_data = ''.join(e for e in callback_data if e.isalnum() or e == '_')
        # print(f"Callback data after: {callback_data}")

        answer_keyboard.append([InlineKeyboardButton(text=answer, callback_data=callback_data)])
    answer_options = InlineKeyboardMarkup(inline_keyboard=answer_keyboard)
    if riddle['image']:
        return await bot.send_photo(user_id, riddle['image'],
                                    caption=riddle['description'], reply_markup=answer_options)
    if riddle['audio']:
        await bot.send_message(user_id, riddle['description'], reply_markup=answer_options)
        return await bot.send_voice(user_id, FSInputFile(riddle['audio']))
    return await bot.send_message(user_id, riddle['description'], reply_markup=answer_options)


@quest_router.callback_query(lambda query: query.data.startswith('answer'))
async def check_inline_answer(callback_query: types.CallbackQuery):
    # option = callback_query.data.split('_')[1]
    next_step = callback_query.data.split('_')[1]
    # print(f"Next step: {next_step}")
    user_id = callback_query.from_user.id
    quest = get_quest(user_id)
    if quest:
        riddles = quests.get(quest.quest_name).get('puzzles')
        step = quest.step
        riddle = riddles[str(step)]
        if riddle['wait']:
            await bot.send_message(user_id, riddle['wait'])
            await asyncio.sleep(1)
        await update_quest(user_id, {"step": int(next_step)})
        await asyncio.sleep(1)
        return await send_quest_step(user_id)
        # distance = Levenshtein.distance(option, riddle['answer'])
        # if distance < 4:    # less than threshold
        #     await bot.send_message(user_id, riddle['wait'])
        #     await update_quest(user_id, {"step": int(next_step)})
        #     await asyncio.sleep(2)
        #     await send_quest_step(user_id)
        # else:
        #     await bot.send_message(user_id, riddle['wait'])
        #     await asyncio.sleep(2)
        #     await bot.send_message(user_id, riddle['exception'].format(answer=option))
    else:
        return await bot.send_message(user_id, responses.get('db_problem'))


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


async def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


@quest_router.message(F.photo)
async def check_photo_answer(message: types.Message):
    user_id = message.from_user.id
    quest = get_quest(user_id)
    if quest:
        riddles = quests.get(quest.quest_name).get('puzzles')
        step = quest.step
        riddle = riddles[str(step)]

        # Assuming you want to use the last photo sent by the user
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = 'images/' + file.file_path.split('.')[-1]
        file_content = await bot.download_file(file.file_path)
        file = open(file_path, 'wb')
        file.write(file_content.getvalue())

        # Assuming you have a function to process the photo
        await bot.send_message(user_id, riddle['wait'])
        answer = predict_image(file_path, model)
        file.close()
        await remove_file(file_path)
        if answer[0] == riddle['answer_photo']:
            await update_quest(user_id, {"step": int(step) + 1})
            return await send_quest_step(user_id)
        else:
            return await bot.send_message(user_id, riddle['exception'].format(answer=message.text.lower()))
    else:
        return await bot.send_message(user_id, responses.get('db_problem'))


@quest_router.message(F.text)
async def check_message_answer(message: types.Message):
    # Checking the answer
    user_id = message.from_user.id
    quest = get_quest(user_id)
    if quest:
        riddles = quests.get(quest.quest_name).get('puzzles')
        step = quest.step
        riddle = riddles[str(step)]

        distance = Levenshtein.distance(message.text.lower(), riddle['answer'])
        if distance < 4:  # less than threshold
            await bot.send_message(user_id, riddle['wait'])
            await update_quest(user_id, {"step": int(step) + 1})
            await asyncio.sleep(2)
            return await send_quest_step(user_id)
        else:
            await bot.send_message(user_id, riddle['wait'])
            await asyncio.sleep(2)
            return await bot.send_message(user_id, riddle['exception'].format(answer=message.text.lower()))
    else:
        return await bot.send_message(user_id, responses.get('db_problem'))
