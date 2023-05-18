from settings import VIP_OPTIONS
from app.database.models import Sponsor

from anypay import Bill
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


def bill(bill: Bill, item_id: str) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Оплатить 🔗',
                    url=bill.url,
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Проверить ✅',
                    callback_data='check:%i:%s' % (
                        bill.id, item_id,
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='Назад 🔙',
                    callback_data='back:vip',
                ),
            ],
        ]
    )

BUY = InlineKeyboardMarkup(
    inline_keyboard=[
        *(
            [
                InlineKeyboardButton(
                    text=item['name'],
                    callback_data='buy:%s' % key,
                ),
            ] for key, item in VIP_OPTIONS.items()
        ),
        [
            InlineKeyboardButton(
                text='Получить бесплатно 🤫',
                callback_data='ref',
            ),
        ],
    ],
)

ADULT_GENDER = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Муж. ♂️',
                callback_data='adult:male',
            ),
            InlineKeyboardButton(
                text='Жен. ♀️',
                callback_data='adult:female',
            ),
        ]
    ],
)

BACK_VIP = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Назад 🔙',
                callback_data='back:vip',
            ),
        ],
    ],
)

PROFILE = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Изменить пол👩‍❤️‍👨',
                callback_data='edit:gender',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Изменить возраст📝',
                callback_data='edit:age',
            ),
        ],
    ],
)
GENDER = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Парень🙋‍♂',
                callback_data='gender:1',
            ),
            InlineKeyboardButton(
                text='Девушка🙎‍♀',
                callback_data='gender:0',
            ),
        ],
    ],
)
