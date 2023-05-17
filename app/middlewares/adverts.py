import json
import time
import random

from app.database.models import History, Advert, User
from app.templates.keyboards.user import reply

from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, Update

from sqlalchemy import or_
from sqlalchemy.future import select


def get_buttons():

    buttons = []

    for row in reply.MENU.dict()['keyboard']:

        for button in row:

            buttons.append(button['text'])

    return buttons


BUTTONS = get_buttons()

class AdMiddleware(BaseMiddleware):
    """
    Middleware for ad showings.
    """

    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any],
    ) -> None:

        await handler(message, data)

        session = data['session']
        config = data['config']
        state = data['state']
        user: User = data['user']
 
        if (
            message.from_user.id in config.bot.admins
            or message.text not in BUTTONS
        ):

            return

        METHODS = (
            message.answer_photo,
            message.answer_video,
            message.answer_animation,
            message.answer_audio,
            message.answer_voice,
        )

        current_time = datetime.now()
        state_data: dict = await state.get_data()
        next_check = state_data.get(
            'next_ad_check', 0,
        )

        if next_check > time.time():

            return

        confirm = await session.scalar(
            select(History).where(
                History.user_id == message.from_user.id,
                History.time > current_time - timedelta(minutes=15),
            )
        )

        if confirm:

            return await state.update_data(
                next_ad_check=confirm.time.timestamp() + 60 * 15,
            )

        adverts = (await session.scalars(
            select(Advert).where(
                Advert.is_active == True,
                or_(
                    Advert.target == 0,
                    Advert.views < Advert.target,
                ),
                Advert.id.notin_(
                    select(History.ad_id).where(
                        History.user_id == message.from_user.id,
                    ),
                ),
            )
        )).all()

        if not adverts:

            return

        ad: Advert = random.choice(adverts)

        if ad.type == 0:

            await message.answer(
                ad.text,
                reply_markup=(
                    json.loads(ad.markup)
                    if ad.markup else None
                ),
                disable_web_page_preview=True,
                disable_notification=True,
            )

        else:

            await METHODS[ad.type - 1](
                ad.file_id,
                caption=ad.text,
                reply_markup=(
                    json.loads(ad.markup)
                    if ad.markup else None
                ),
                disable_notification=True,
            )

        session.add(
            History(
                user_id=message.from_user.id,
                ad_id=ad.id,
            ),
        )
        ad.views += 1
        await session.commit()
        
        await state.update_data(
            next_ad_check=time.time() + 15 * 60,
        )
