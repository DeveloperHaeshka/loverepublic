import time
import asyncio

from app.templates.keyboards import admin as nav

from typing import Optional
from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter


class MailerSingleton(object):

    SPEED = 25

    __tasks: list[asyncio.Future] = []
    __semaphore = asyncio.Semaphore(SPEED)
    __instance = None


    def __init__(self) -> None:
        """
        Creator of MailerSingleton. Raises an exception if an instance already exists.

        :param int | float delay: Delay between messages, optional.
        :raises Exception: If an instance already exists.
        """

        if MailerSingleton.__instance is not None:

            raise Exception('MailingSingleton is a singleton!')

        MailerSingleton.__instance = self


    @staticmethod
    def get_instance() -> 'MailerSingleton':
        """
        Get an instance of MailerSingleton.

        :return MailerSingleton: Already existing / newly created instance.
        """

        if MailerSingleton.__instance is None:

            MailerSingleton()

        return MailerSingleton.__instance


    @staticmethod
    def pretty_time(seconds: float) -> str:
        """
        Get a pretty time string.

        :param float seconds: UNIX timestamp.
        :return str: Time in hunan-readable format.
        """

        seconds = int(seconds)

        return '%0d:%0d:%0d' % (
            seconds // 3600,
            seconds % 3600 // 60,
            seconds % 60
        )


    def get_text(self) -> str:
        """
        Get an ETA message.

        :return str: Ready message.
        """

        progress = int((self.progress or 1) / self.length * 25)
        progress_bar = ('=' * progress) + (' ' * (25 - progress))

        return "<code>[%s]</> %s/%s (ETA: %s)" % (
            progress_bar,
            self.progress,
            self.length,
            self.pretty_time((self.length - self.progress) / self.SPEED)
        )


    async def start_mailing(
        self, 
        bot: Bot, 
        message_id: int, 
        chat_id: int, 
        reply_markup: Optional[dict], 
        scope: list[int], 
    ):
        """
        Start mailing.

        :param Bot bot: An instance of Bot.
        :param int message_id: Target message ID.
        :param int chat_id: Target chat ID.
        :param Optional[dict] reply_markup: Target message reply markup.
        :param list[int] scope: Users to send to.
        """

        self.stop_mailing()
        
        self.last_update = time.monotonic()
        
        self.blocked = 0
        self.progress = 0
        self.length = len(scope)

        self.bot = bot
        self.message_id = message_id
        self.chat_id = chat_id
        self.reply_markup = reply_markup

        self.admin_message = await bot.send_message(
            chat_id,
            self.get_text(),
            reply_markup=nav.inline.STOPMAIL,
        )

        await asyncio.gather(
            *(
                self._mail(user_id)
                for user_id in scope
            )
        )

        with suppress(TelegramAPIError):
            
            await self.admin_message.edit_text(self.get_text())

        await self.admin_message.answer(
            'Рассылка завершена. Успешно: %s. Бот заблокирован: %s' % (
                (len(scope) - self.blocked), self.blocked,
            ),
        )


    async def _mail(self, user_id: int) -> None:

        async with self.__semaphore:

            if self.last_update + 5 < time.time():

                self.last_update = time.time()

                with suppress(TelegramAPIError):
                    
                    await self.admin_message.edit_text(self.get_text())

            start_time = time.perf_counter()
            self.progress += 1
            
            try:

                await self.bot.copy_message(
                    message_id=self.message_id,
                    from_chat_id=self.chat_id,
                    chat_id=user_id,
                    reply_markup=self.reply_markup,
                )

            except TelegramRetryAfter as exc:

                await asyncio.sleep(exc.retry_after)

            except TelegramAPIError:

                self.blocked += 1

            sleep_time = 1 - (start_time - time.perf_counter()) / 10 ** 9
            await asyncio.sleep(max(sleep_time, 0))


    def stop_mailing(self) -> bool:
        """
        Stops mailing. Returns True on success.

        :return bool: True on successful stop.
        """
        
        for task in self.__tasks:
            
            task.cancel()

        self.__tasks.clear()

        return True


    @property
    def is_mailing(self) -> bool:
        """
        Check if mailing is in progress.

        :return bool: True if mailing is in progress.
        """

        return bool(self.__tasks)
