import os
import time
import logging

from app import middlewares, handlers, database
from app.utils import set_commands, load_config, schedule
from app.utils.config import Settings
from app.utils.payments import PayOk
from app.utils.nudes import NudesAPI

from aiohttp.web import Application, run_app

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker


log = logging.getLogger(__name__)

async def on_startup(bot: Bot, config: Settings, sessionmaker: async_sessionmaker, engine: AsyncEngine):

    await bot.set_webhook(config.webhook.url + config.bot.token)

    bot_info = await bot.me()
    log.info('Set webhook for @%s' % bot_info.username)

    await database.create_tables(engine)
    
    await set_commands(bot, config, sessionmaker)
    await schedule.setup(bot, sessionmaker)


async def on_shutdown(bot: Bot):

    await bot.delete_webhook()


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)

    log.info("Starting bot...")
    config = load_config()

    os.environ['TZ'] = config.bot.timezone
    time.tzset()
    log.info('Set timesone to "%s"' % config.bot.timezone)

    if config.bot.use_redis:

        storage = RedisStorage.from_url(
            'redis://%s:6379/%i' % (
                config.redis.host,
                config.redis.db,
            ),
        )

    else:

        storage = MemoryStorage()

    engine = database.create_engine(config.db)
    sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    bot = Bot(
        token=config.bot.token,
        parse_mode="HTML",
    )
    payok = PayOk(
        config.payments.project_id,
        config.payments.project_secret,
        sessionmaker,
        bot,
    )

    dp = Dispatcher(storage=storage, config=config, engine=engine, sessionmaker=sessionmaker, payment=payok)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    middlewares.setup(dp, sessionmaker)
    handlers.setup(dp)

    app = Application()
    app["bot"] = bot

    SimpleRequestHandler(
        dispatcher=dp, bot=bot,
    ).register(app, path='/' + config.bot.token)
    setup_application(app, dp, bot=bot)

    app.router.add_post('/payok', payok.handle_bill)
    app.router.add_post('/nudes', NudesAPI.process)

    run_app(app, host='0.0.0.0', port=config.webhook.port)


try:

    main()

except (
    KeyboardInterrupt,
    SystemExit,
):

    log.critical("Bot stopped")
