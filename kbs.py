from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Those buttons are below user input box
kb_client = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🧩Маҗаралар🧩"),
            KeyboardButton(text="👍Фидбәк👎"),
        ],
        [
            KeyboardButton(text="🙏Ярдәм🙏"),
            KeyboardButton(text="🏅Ачивкалар🏅"),
        ],
        [
            KeyboardButton(text="👑Түләүле квестлар👑"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)
