from app.database.models import Sponsor

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def split(items: list, size: int) -> list[list]:

    return [
        items[index:index + size] 
        for index in range(0, len(items), size)
    ]


def subscription(sponsors: list[Sponsor]) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            *(
                [
                    InlineKeyboardButton(
                        text=sponsor.title,
                        url=sponsor.link,
                    ),
                ] for sponsor in sponsors
            ),
            [
                InlineKeyboardButton(
                    text='Проверить подписку',
                    callback_data='checksub',
                ),
            ],
        ]
    )


def invite(username: str, user_id: int) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Поделиться',
                    url='https://t.me/share/url?url=https://t.me/%s?start=%i&text=То%%20самое%%20API%%20для%%20раздевания%%20девушек%%20☝️' % (
                        username,
                        user_id,
                    ),
                ),
            ],
        ],
    )


def bill(url: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Оплатить 🟢',
                    url=url,
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад 🔙',
                    callback_data='prices',
                ),
            ],
        ],
    )


PROFILE = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Пополнить баланс',
                callback_data='prices',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Сбросить ключ',
                callback_data='reset',
            ),
        ],
    ],
)

PRICES = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='100р',
                callback_data='buy:100',
            ),
            InlineKeyboardButton(
                text='250р',
                callback_data='buy:250',
            ),
        ],
        [
            InlineKeyboardButton(
                text='500р',
                callback_data='buy:500',
            ),
            InlineKeyboardButton(
                text='1000р',
                callback_data='buy:1000',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Своя сумма',
                callback_data='buy:custom',
            ),
        ],
    ],
)
PRICES_BACK = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад 🔙',
                callback_data='prices',
            ),
        ],
    ],
)

CANCEL = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад 🔙',
                callback_data='cancel',
            ),
        ],
    ],
)
