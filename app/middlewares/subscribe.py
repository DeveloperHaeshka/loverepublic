import time
import aiohttp
import asyncio

from app.utils.config import Settings
from app.database.models import User, Sponsor

from functools import lru_cache
from contextlib import suppress
from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, Chat
from aiogram.exceptions import (
    TelegramNotFound,
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramAPIError,
)
from aiogram.fsm.context import FSMContext
from aiogram.utils.token import TokenValidationError

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class SubMiddleware(BaseMiddleware):
    """
    Middleware for checking user's subscription
    """

    def __init__(self):

        self.session = aiohttp.ClientSession()


    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:

        user: Optional[User] = data.get('user')
        config: Settings = data['config']
        state: FSMContext = data['state']
        session: AsyncSession = data['session']

        chat: Optional[Chat] = data.get('event_chat')

        if not chat or getattr(user, 'id', 0) in config.bot.admins or getattr(user, 'is_admin', False):  # opted for safer check

            return await handler(event, data)

        state_data = await state.get_data()
        time_to_check: bool = state_data.get('lask_check', 0) < (time.time() - 60)

        if not time_to_check or chat.type != 'private' or getattr(user, 'is_vip', False):

            return await handler(event, data)

        user = user or data.get('event_from_user')

        sponsors = await session.scalars(
            select(Sponsor)
            .where(Sponsor.is_active == True)
        )
        available_sponsors = await self.get_sponsors(sponsors, user, data['bot'])

        if not available_sponsors:
                    
            await state.update_data(
                last_check=time.time(),
            )

        data['sponsors'] = available_sponsors
        return await handler(event, data)


    async def get_sponsors(self, sponsors: list[Sponsor], user: User, bot: Bot) -> list[Sponsor]:

        response = await asyncio.gather(
            *(
                self._check_sub(sponsor, user, bot)
                for sponsor in [
                    obj for obj in sponsors
                    if obj.check
                ]
            ),
        )
        not_subbed = [
            sponsor for sponsor in response
            if sponsor is not None
        ]

        if bool(not_subbed):

            return not_subbed + [
                sponsor for sponsor in sponsors 
                if not sponsor.check
            ]

        return []


    async def _check_sub(self, sponsor: Sponsor, user: User, bot: Bot) -> Optional[Sponsor]:

        if sponsor.is_bot:
            
            try:

                bot_ = Bot(sponsor.access_id, session=bot.session)
                await bot_.send_chat_action(user.id, 'typing')

            except TokenValidationError:

                with suppress(ValueError):

                    self._validate_botstat_token(sponsor.access_id)

                    async with self.session.get(
                        'https://api.botstat.io/checksub/%s/%i' % (
                            sponsor.access_id, user.id,
                        )
                    ) as response:

                        data = await response.json(content_type=None)

                        if not data['ok']:

                            return sponsor

            except (
                TelegramNotFound,
                TelegramBadRequest,
                TelegramForbiddenError,
            ):
            
                return sponsor

        else:

            with suppress(TelegramAPIError):

                member = await bot.get_chat_member(
                    sponsor.access_id,
                    user.id,
                )

                if member.status in ('left', 'kicked', None):

                    return sponsor


    @staticmethod
    @lru_cache
    def _validate_botstat_token(token: str):

        if len(token.split('-')) != 5:

            raise ValueError
