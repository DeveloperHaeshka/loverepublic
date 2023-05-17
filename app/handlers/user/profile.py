import uuid
import psutil

from app.templates import texts
from app.templates.keyboards import user as nav
from app.database.models import User
from app.utils.payments import PayOk
from app.utils.config import Settings
from app.utils.nudes import NudesAPI, NudesAPIError

from aiogram import Router, Bot, types
from aiogram.filters import Text, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession


async def profile(update: types.Message | types.CallbackQuery, user: User):

    method = (
        update.answer if isinstance(update, types.Message)
        else update.message.edit_text
    )

    await method(
        texts.user.PROFILE % (
            user.id,
            user.balance,
            int(user.balance / 4),
            user.api_key,
        ),
        reply_markup=nav.inline.PROFILE,
    )


async def reset_key(call: types.CallbackQuery, user: User, session: AsyncSession):

    user.api_key = uuid.uuid4()
    await session.commit()

    await call.answer('Ключ изменен!', True)
    await profile(call, user)


async def examples(message: types.Message):

    await message.answer_media_group(
        [
            types.InputMediaPhoto(
                media='https://telegra.ph/file/6a80c45a4f086ca213222.jpg',
                caption='Примеры работы нашего API 👆\n\n<i>В силу ограничений telegram была применена цензура</>',
            ),
            types.InputMediaPhoto(
                media='https://telegra.ph/file/682fb12680df05e340fee.jpg',
            ),
            types.InputMediaPhoto(
                media='https://telegra.ph/file/682fb12680df05e340fee.jpg',
            ),
        ],
    )


async def prices(message: types.Message, user: User):
    
    await message.answer(
        texts.user.PRICES % (
            user.balance,
            int(user.balance / 4),
        ),
        reply_markup=nav.inline.PRICES,
    )


async def prices_cb(call: types.CallbackQuery, state: FSMContext, user: User):

    await state.set_state()

    await call.message.edit_text(
        texts.user.PRICES % (
            user.balance,
            int(user.balance / 4),
        ),
        reply_markup=nav.inline.PRICES,
    )


async def buy(call: types.CallbackQuery, state: FSMContext, payment: PayOk):

    amount = call.data.split(':')[1]

    if not amount.isdigit():

        await state.set_state('buy.custom')
        return await call.message.edit_text(
            'Введите сумму пополнения (от 100р):',
            reply_markup=nav.inline.PRICES_BACK,
        )

    bill = payment.create_bill(int(amount), call.from_user.id)
    await call.message.edit_text(
        'Оплатить пополнение можно по ссылке ниже:',
        reply_markup=nav.inline.bill(bill),
    )


async def buy_custom(message: types.Message, payment: PayOk):

    try:

        amount = int(message.text)

        if amount < 1: 

            raise ValueError

    except ValueError:

        return await message.answer(
            'Введите корректное число (от 100р):',
            reply_markup=nav.inline.PRICES_BACK,
        )

    bill = payment.create_bill(amount, message.from_user.id)
    await message.answer(
        'Оплатить пополнение можно по ссылке ниже:',
        reply_markup=nav.inline.bill(bill),
    )


async def referral(message: types.Message, bot_info: types.User, user: User):

    await message.answer(
        texts.user.REF % (
            bot_info.username,
            user.id,
            user.ref_balance,
        ),
        reply_markup=nav.inline.invite(bot_info.username, user.id),
    )


async def server_status(messsage: types.Message):

    await messsage.answer(
        texts.user.load(
            psutil.cpu_percent(interval=None),
            psutil.virtual_memory(),
        ),
    )


async def pre_demo(message: types.Message, state: FSMContext, user: User):

    await state.set_state('demo.image')
    await message.answer(
        'Пришлите фотографию, которую хотите раздеть. Запрос будет сделан с вашим токеном.',
        reply_markup=nav.inline.CANCEL,
    )


async def demo(message: types.Message, state: FSMContext, bot: Bot, user: User, config: Settings):

    if not message.photo:

        return await message.answer(
            'Это не фото!',
            reply_markup=nav.inline.CANCEL,
        )

    await state.set_state()

    msg = await message.answer('Загружаю фото...')
    file = await bot.get_file(message.photo[-1].file_id)

    try:

        await NudesAPI.create_task(file.file_path, str(user.api_key), user.id, config.webhook.url)

    except NudesAPIError as exc:

        return await msg.edit_text('Возникла ошибка: <code>%s</>' % exc.message) 

    await msg.edit_text('Задача на создание фото постановлена. Ожидайте, ETA - 3 минуты.')


async def cancel(call: types.CallbackQuery, state: FSMContext):

    await state.set_state()
    await call.message.edit_text('❌ Действие отменено')


def register(router: Router):

    router.message.register(profile, Text('Профиль'))
    router.callback_query.register(reset_key, Text('reset'))

    router.message.register(examples, Text('Примеры'))

    router.message.register(prices, Text('Цены'))
    router.callback_query.register(prices_cb, Text('prices'))
    
    router.callback_query.register(buy, Text(startswith='buy:'))
    router.message.register(buy_custom, StateFilter('buy.custom'))

    router.message.register(referral, Text('Партнерка'))

    router.message.register(server_status, Text('Статус'))

    router.message.register(pre_demo, Text('Демо'))
    router.message.register(demo, StateFilter('demo.image'))

    router.callback_query.register(cancel, Text('cancel'))
