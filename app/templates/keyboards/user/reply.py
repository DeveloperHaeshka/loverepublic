from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Примеры'),
            KeyboardButton(text='Профиль'),
        ],
        [
            KeyboardButton(text='Цены'),
            KeyboardButton(text='Партнерка'),
        ],
        [
            KeyboardButton(text='Статус'),
            KeyboardButton(text='Демо'),
        ],
    ],
    resize_keyboard=True,
)

JOIN_REQUEST = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🛥️'),
            KeyboardButton(text='👾'),
            KeyboardButton(text='🏎️'),
        ],
        [
            KeyboardButton(text='🌐'),
            KeyboardButton(text='🛩️'),
            KeyboardButton(text='⏳'),
        ],
    ]   
)
