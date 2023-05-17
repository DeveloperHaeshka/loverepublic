import asyncio

from contextlib import suppress

from aiohttp import ClientSession, web

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter


class NudesAPIError(Exception):

    def __init__(self, message: str):

        self.message = message
        super().__init__(message)


class NudesAPI(object):

    @staticmethod
    async def create_task(url: str, token: str, user_id: int, webhook_url: str):

        # temp
        raise NudesAPIError('API находится в разработке')

        async with ClientSession() as session:

            async with session.post(
                'https://api.deepnudes.su/getFull',
                json={
                    'token': token,
                    'url': url,
                    'user_id': user_id,
                    'webhook': webhook_url + 'nudes',
                },
            ) as response:

                data = await response.json(content_type=None)

                if not response.ok:

                    raise NudesAPIError(data.get('error'))

                return data


    @classmethod
    async def process(cls, request: web.Request) -> web.Response:

        bot: Bot = request.app['bot']
        data = await request.json()

        with suppress(TelegramAPIError):

            try:

                await bot.send_photo(
                    data.get('user_id', 0), 
                    data.get('photo_url'),
                )

            except TelegramRetryAfter as exc:

                asyncio.create_task(
                    cls.process_retry(
                        data,
                        bot,
                        exc.retry_after,
                    ),
                )

        return web.Response(status=200)


    @classmethod
    async def process_retry(cls, data: dict, bot: Bot, retry_after: int) -> None:

        await asyncio.sleep(retry_after)

        with suppress(TelegramAPIError):

            try:

                await bot.send_photo(
                    data.get('user_id', 0), 
                    data.get('photo_url'),
                )

            except TelegramRetryAfter as exc:

                asyncio.create_task(
                    cls.process_retry(
                        data, 
                        bot,
                        exc.retry_after,
                    ),
                )
