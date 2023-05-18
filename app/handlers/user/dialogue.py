import json

from app.filters import InDialogue, IsVip
from app.database.models import User, Dialogue, Queue, History, Advert
from app.templates import texts
from app.templates.keyboards import user as nav

from typing import Optional
from datetime import datetime, timedelta
from contextlib import suppress

from aiogram import Router, Bot, types
from aiogram.filters import Text, Command
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.fsm.context import FSMContext

from sqlalchemy import delete, or_, func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def show_ad(bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    if user.is_vip:

        return

    METHODS = (
        None,
        bot.send_photo,
        bot.send_video,
        bot.send_animation,
        bot.send_audio,
        bot.send_voice,
    )

    current_time = datetime.now()
    state_data = await state.get_data()
    next_check = state_data.get(
        'next_ad_check', datetime.fromtimestamp(0),
    )

    if next_check > current_time:

        return

    confirm = await session.scalar(
        select(History).where(
            History.user_id == user.id,
            History.time > current_time - timedelta(minutes=15),
        )
    )

    if confirm:

        return await state.update_data(
            next_ad_check=confirm.time + timedelta(minutes=15),
        )

    ad = await session.scalar(
        select(Advert)
        .where(
            Advert.is_active,
            or_(
                Advert.target == 0,
                Advert.views < Advert.target,
            ),
            Advert.id.notin_(
                select(History.ad_id)
                .where(History.user_id == user.id)
            ),
        )
        .order_by(func.random())
    )

    if not ad:

        return

    if ad.type == 0:

        await bot.send_message(
            user.id,
            ad.text,
            reply_markup=(
                json.loads(ad.markup)
                if ad.markup else None
            ),
            disable_web_page_preview=True,
            disable_notification=True,
        )

    else:

        await METHODS[ad.type](
            user.id,
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
            user_id=user.id,
            ad_id=ad.id,
        ),
    )
    ad.views += 1

    await session.commit()
    await state.update_data(
        next_ad_check=current_time + timedelta(minutes=15),
    )


async def queue(bot: Bot, session: AsyncSession, user: User, state: FSMContext, target_man: Optional[bool]=None, is_adult: bool=False):

    stmt = select(Queue) \
        .where(Queue.id != user.id) \
        .where(Queue.is_adult == is_adult) \
        .where(
            or_(
                Queue.target_man == user.is_man,
                Queue.target_man == None,
            ),
        )

    if target_man is not None:

        stmt = stmt.where(Queue.is_man == target_man)

    await state.update_data(
        is_adult=is_adult,
        target_man=target_man,
    )
    match = await session.scalar(stmt)

    if match:

        return await create_dialogue(bot, session, user.id, match.id)

    await session.execute(
        delete(Queue)
        .where(Queue.id == user.id)
    )
    session.add(
        Queue(
            id=user.id,
            is_man=user.is_man,
            target_man=target_man,
            is_adult=is_adult,
        )
    )
    await session.commit()

    await bot.send_message(
        user.id,
        texts.user.DIALOGUE_SEARCH,
    )


async def create_dialogue(bot: Bot, session: AsyncSession, first: int, second: int):

    for user_id in (first, second):

        with suppress(TelegramAPIError):

            await bot.send_message(
                user_id,
                texts.user.DIALOGUE_FOUND,
                reply_markup=nav.reply.END_DIALOGUE,
            )

    await session.execute(
        delete(Queue)
        .where(Queue.id.in_((first, second)))
    )
    session.add(
        Dialogue(
            first=first,
            second=second,
        )
    )
    await session.commit()


async def delete_dialogue(session: AsyncSession, user_id: int):

    await session.execute(
        delete(Dialogue)
        .where(
            or_(
                Dialogue.first == user_id,
                Dialogue.second == user_id,
            ),
        )
    )
    await session.commit()


async def finish_dialogue(message: types.Message, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    await message.answer(
        texts.user.DIALOGUE_END if user.partner else texts.user.SEARCH_END,
        reply_markup=nav.reply.main_menu(user),
    )
    await show_ad(bot, state, session, user)

    await session.execute(
        delete(Queue)
        .where(Queue.id == user.id)
    )

    if not user.partner:

        return await session.commit()

    second_user = await session.get(User, user.partner_id)
    await delete_dialogue(session, user.id)

    if not second_user: 

        return

    with suppress(TelegramAPIError):

        await bot.send_message(
            second_user.id,
            texts.user.DIALOGUE_END,
            reply_markup=nav.reply.main_menu(second_user),
        )

    await show_ad(bot, state, session, second_user)


async def forward_message(message: types.Message, session: AsyncSession, user: User):

    try:

        await message.copy_to(user.partner_id)

    except TelegramBadRequest:

        await message.answer('Ваш собеседник заблокировал бота, диалог окончен!')
        await delete_dialogue(session, user.id)


async def random_normal(_, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    await queue(bot, session, user, state=state)


async def male_normal(_, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    await queue(bot, session, user, target_man=True, state=state)


async def female_normal(_, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    await queue(bot, session, user, target_man=False, state=state)


async def pre_adult(message: types.Message):

    await message.answer(
        texts.user.DIALOGUE_GENDER,
        reply_markup=nav.inline.ADULT_GENDER,
    )


async def adult(call: types.CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    target = call.data.split(':')[1]

    await call.message.delete()
    await queue(bot, session, user, target_man=target == 'male', is_adult=True, state=state)


async def next(message: types.Message, bot: Bot, state: FSMContext, session: AsyncSession, user: User):

    if user.partner:

        await finish_dialogue(message, bot, state, session, user)

    state_data = await state.get_data()    
    await queue(
        bot, session, user, state=state,
        target_man=state_data.get('target_man'), 
        is_adult=state_data.get('is_adult', False), 
    )


def register(router: Router):

    router.message.register(random_normal, Text('Начать диалог 🔍'))

    router.message.register(male_normal, Text('Поиск М 👨'))
    router.message.register(female_normal, Text('Поиск Ж 👩'))

    router.message.register(pre_adult, Text('Пошлый чат 🔞'))
    router.callback_query.register(adult, Text(startswith='adult:'), IsVip())

    router.message.register(next, Command('next'))

    router.message.register(finish_dialogue, Command('stop'))
    router.message.register(finish_dialogue, Text('Завершить диалог 🚫'))

    router.message.register(forward_message, InDialogue())
