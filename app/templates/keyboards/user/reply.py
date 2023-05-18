from app.database.models import User

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu(user: User) -> ReplyKeyboardMarkup:

    if user.is_vip:

        return VIP_MENU

    return USER_MENU


VIP_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Начать диалог 🔍'),
        ],        
        [
            KeyboardButton(text='Поиск Ж 👩'),
            KeyboardButton(text='Поиск М 👨'),
        ],
        [
            KeyboardButton(text='Пошлый чат 🔞'),
            KeyboardButton(text='Профиль 👤'),
        ],
        [
            KeyboardButton(text='VIP 👑'),
        ], 
    ],
    resize_keyboard=True,
)
USER_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Начать диалог 🔍'),
        ],
        [
            KeyboardButton(text='Поиск по полу ♂️'),
        ],
        [
            KeyboardButton(text='Пошлый чат 🔞'),
            KeyboardButton(text='Профиль 👤'),
        ],
        [
            KeyboardButton(text='VIP 👑'),
        ],
    ], 
    resize_keyboard=True,
)

END_DIALOGUE = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Завершить диалог 🚫'),
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
    ],  
)
