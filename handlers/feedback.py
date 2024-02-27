from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils import get_completed_quests, safe_feedback

router = Router()


class FeedbackStates(StatesGroup):
    choose_completed_quest = State()
    rate_quest = State()
    provide_feedback = State()


@router.message(lambda message: message.text.lower() == '👍feedback👎')
async def choose_quest(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    quests = get_completed_quests(user_id)
    if quests:
        answer_keyboard = []
        for quest in quests:
            answer_keyboard.append([types.InlineKeyboardButton(text=quest, callback_data=f"quest_{quest.quest_name}")])
        await message.answer("Which quest did you finish?",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=answer_keyboard))
        await state.set_state(FeedbackStates.choose_completed_quest)
    else:
        await message.answer("Вы еще не прошли квест 🥺. Возвратитесь к нам после завершения квеста")
    await state.set_state(FeedbackStates.choose_completed_quest)


@router.callback_query(FeedbackStates.choose_completed_quest, lambda message: message.text.startswith('quest_'))
async def choose_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(chosen_quest=callback_query.data.split('_')[1])
    rates = [[types.InlineKeyboardButton(text=str("⭐" * i), callback_data=f"rating_{i}")] for i in range(1, 6)]
    await callback_query.message.edit_text("Please rate your satisfaction from 1 to 5 stars:",
                                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=rates))
    await state.set_state(FeedbackStates.rate_quest)


@router.callback_query(FeedbackStates.rate_quest, lambda message: message.text.startswith('rating_'))
async def provide_feedback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(rating=int(callback_query.data.split('_')[1]))
    await callback_query.message.edit_text("Спасибо🙏 за вашу оценку! Пожалуйста, можете еще оставить письменный фидбек (напр. 'интересно...', 'ужасно(...'")
    await state.set_state(FeedbackStates.provide_feedback)


@router.message(FeedbackStates.provide_feedback)
async def save_feedback(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chosen_quest = data.get('quest_name')
    rating = data.get('rating')
    user_id, feedback_text = message.from_user.id, message.text
    await safe_feedback(user_id, choose_quest, rating, feedback_text)
    await message.answer("Спасибо за ваш фидбэк!")
    await state.clear()
