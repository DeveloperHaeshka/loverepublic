from app.database.models import User, Referral
from app.utils.text import get_ref

from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware, types
from aiogram.types import Update

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserMiddleware(BaseMiddleware):
    """
    Middleware for registering user.
    """

    async def __call__(
        self, 
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:

        event_user: Optional[types.User] = data.get("event_from_user")
        event_chat: Optional[types.Chat] = data.get("event_chat")

        if not event_user or event.chat_join_request:

            return await handler(event, data)

        session: AsyncSession = data['session']
        user = await session.scalar(
            select(User)
            .where(User.id == event_user.id)
        )

        if not user and not event.inline_query:

            ref = None

            if getattr(event.message, 'text', False):

                link = get_ref(event.message)

                if link:
                
                    referral = await session.scalar(
                        select(Referral)
                        .where(Referral.ref == link)
                    )

                    if referral:

                        ref = referral.ref

            user = User(
                id=event_user.id,
                ref=ref,
                chat_only=getattr(event_chat, 'type', None) != 'private',
            )
            session.add(user)
            
            await session.commit()

        elif getattr(event_chat, 'type', None) == 'private' and user.chat_only:

            user.chat_only = False
            await session.commit()

        data["user"] = user

        return await handler(event, data)
