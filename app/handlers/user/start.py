from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import Referral

from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


async def start(message: types.Message, command: CommandObject, bot_info: types.User, session: AsyncSession):

    await message.answer(
        texts.user.START % bot_info.username,
        reply_markup=nav.reply.MENU,
    )

    if not command.args:

        return

    await session.execute(
        update(Referral)
        .where(Referral.ref == command.args)
        .values(total=Referral.total + 1)
    )
    await session.commit()


def register(router: Router):

    router.message.register(start, CommandStart())
