from app.utils import set_commands
from app.utils.config import Settings
from app.database.models import User
from app.templates.keyboards import admin as nav

from aiogram import Router, Bot, types
from aiogram.filters import CommandStart, Command

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def start(message: types.Message):

    await message.answer(
        'Админ-панель',
        reply_markup=nav.reply.MENU,
    )


async def give_admin(message: types.Message, bot: Bot, session: AsyncSession, config: Settings):

    if message.from_user.id not in config.bot.admins:

        return

    try:

        user_id = int(message.text.split(' ')[1])

    except (IndexError, ValueError):

        return await message.answer(
            'Пример использования команды: <code>/admin &lt;user_id&gt;</code>',
        )

    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
    )

    if not user:

        return await message.answer(
            'Пользователь с таким id не найден в базе.',
        )

    user.is_admin = not user.is_admin
    await session.commit()

    await message.answer(
        '%s админку пользователя %i' % (
            ('Выдал' if user.is_admin else 'Убрал'),
            user.id,
        ),
    )
    await set_commands(bot, config, session=session)


def register(router: Router):

    router.message.register(start, CommandStart())
    router.message.register(give_admin, Command('admin'))
