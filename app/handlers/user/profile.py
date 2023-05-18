from app.templates import texts
from app.utils.text import escape
from app.database.models import User
from app.templates.keyboards import user as nav

from contextlib import suppress

from aiogram import Router, types
from aiogram.filters import Command, Text, StateFilter
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession


async def show_profile(message: types.Message, user: User):

    await message.answer(
        texts.user.PROFILE % (
            escape(message.from_user.full_name),
            ('Мужской' if user.is_man else 'Женский'),
            user.age,
            ('есть' if user.is_vip else 'нет'),
        ),
        reply_markup=nav.inline.PROFILE,
    )


async def pre_edit_profile(call: types.CallbackQuery, state: FSMContext):

    action = call.data.split(':')[1]

    if action == 'age':

        await call.message.edit_text('<i>Введите ваш возраст:</>')
        await state.set_state('edit.age')

    else:

        await call.message.edit_text(
            '<i>Выберите ваш пол:</>',
            reply_markup=nav.inline.GENDER,
        )


async def edit_gender(call: types.CallbackQuery, user: User, state: FSMContext, session):

    user.is_man = bool(int(call.data.split(':')[1]))
    await session.commit()

    if not user.age:

        with suppress(TelegramAPIError):

            await call.message.edit_text('<i>Теперь напиши свой возраст! (от 16 до 99)</>')

        await state.set_state('edit.age')

    else:

        await call.message.edit_text(
            texts.user.PROFILE % (
                escape(call.from_user.full_name),
                ('Мужской' if user.is_man else 'Женский'),
                user.age,
                ('есть' if user.is_vip else 'нет'),
            ),
            reply_markup=nav.inline.PROFILE,
        )


async def edit_age(message: types.Message, state: FSMContext, session: AsyncSession, user: User):

    try:

        age = int(message.text)

        if age < 16 or age > 99:

            raise ValueError

    except ValueError:

        return await message.answer('<i>Введите корректный возраст.</>')

    prev_age = user.age

    user.age = age
    await session.commit()
    await state.clear()

    if not prev_age:

        return await message.answer(
            texts.user.START,
            reply_markup=nav.reply.main_menu(user),
        )

    await show_profile(message, user)


def register(router: Router):

    router.message.register(show_profile, Command('profile'))
    router.message.register(show_profile, Text('Профиль 👤'))

    router.callback_query.register(pre_edit_profile, Text(startswith='edit:'))

    router.callback_query.register(edit_gender, Text(startswith='gender:'))
    router.message.register(edit_age, StateFilter('edit.age'))
