import time
import logging
import hashlib

from app.database.models import User, Bill

from contextlib import suppress
from urllib.parse import urlencode

from aiohttp import web

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


log = logging.getLogger('payments')

class PayOk(object):

    CURRENCY = 'RUB'
    DESCRIPTION = 'Пополнения баланса'

    def __init__(self, project_id: int, project_secret: str, sessionmaker: async_sessionmaker, bot: Bot):

        self.project_id = project_id
        self.project_secret = project_secret

        self.sessionmaker = sessionmaker
        self.bot = bot


    def _create_signature(self, amount: int, payment_id: int, reverse: bool=False) -> str:

        parameters = [amount, payment_id, self.project_id, self.CURRENCY, self.DESCRIPTION, self.project_secret]

        if reverse:

            parameters.reverse()

        sign_params = '|'.join(map(
            str,
            parameters,    
        )).encode('utf-8')
        return hashlib.md5(sign_params).hexdigest()


    def create_bill(self, amount: int, user_id: int) -> str:

        payment_id = int(time.time())
        params = {
            'amount': amount,
            'payment': payment_id,
            'shop': self.project_id,
            'currency': self.CURRENCY,
            'desc': self.DESCRIPTION,
            'user_id': user_id,
            'sign': self._create_signature(amount, payment_id),
        }
        
        return 'https://payok.io/pay?' + urlencode(params)


    async def _process_payment(self, data: dict, session: AsyncSession) -> None:

        bill_id = int(data['payment_id'])
        user_id = int(data.get('custom[user_id]', 0))
        amount = int(data['profit'])

        session.add(
            Bill(
                id=bill_id,
                user_id=user_id,
                amount=amount,
            ),
        )

        user = await session.scalar(
            select(User)
            .where(User.id == user_id)
        )

        if user:

            user.balance += amount
            ref = user.ref or ''

            with suppress(TelegramAPIError):

                await self.bot.send_message(
                    user.id,
                    '✅ На ваш баланс зачислено %s руб' % amount,
                )

            if ref.isdigit():
            
                await session.execute(
                    update(User)
                    .where(User.id == int(ref))
                    .values(ref_balance=User.ref_balance + int(amount * 0.1))
                )

        await session.commit()
    

    async def handle_bill(self, request: web.Request):

        data: dict = dict(await request.post())
        computed_sign = self._create_signature(
            data.get('amount'),
            data.get('payment_id'),
            reverse=True,
        )

        if data.get('sign') != computed_sign:

            log.warning('Request with incorrect signature')
            return web.Response(status=403)

        bill_id = int(data['payment_id'])
        log.info('New payment for %s rub.' % data['profit'])

        async with self.sessionmaker() as session:

            bill = await session.get(Bill, bill_id)

            if not bill:

                await self._process_payment(data, session)

        return web.Response(status=200)
