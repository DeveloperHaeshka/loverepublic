from aiogram.types import BotCommand

ADMIN_COMMANDS = [
    BotCommand(
        command="start", 
        description="Запустить бота",
    ),
    BotCommand(
        command="stats", 
        description="Статистика",
    ),
    BotCommand(
        command="stats", 
        description="Прибыль",
    ),
    BotCommand(
        command="dump", 
        description="Выгрузка",
    ),
    BotCommand(
        command="mailing", 
        description="Рассылка",
    ),
    BotCommand(
        command="referrals", 
        description="Рефералы",
    ),
    BotCommand(
        command="sponsors", 
        description="Спонсоры",
    ),
    BotCommand(
        command="adverts", 
        description="Реклама",
    ),
    BotCommand(
        command="requests", 
        description="Заявки",
    ),
    BotCommand(
        command="admin", 
        description="Выдать / убрать админку",
    ),
]
