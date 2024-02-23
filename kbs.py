from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Those buttons are below user input box
kb_client = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Квесты"),
            KeyboardButton(text="Feedback"),
        ],
        [
            KeyboardButton(text="Помощь"),
            KeyboardButton(text="Результаты"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
