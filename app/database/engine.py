import logging

from app.utils.config import DB
from app.database.models import Base

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


log = logging.getLogger('database.engine')

async def create_tables(engine: AsyncEngine) -> None:
    """
    Create tables from models. 

    :param AsyncSession session: Async Sess
    """
    
    async with engine.begin() as conn:
            
        await conn.run_sync(Base.metadata.create_all)

        log.info('Tables created successfully')


def create_engine(database: DB) -> AsyncEngine:
    """
    Create an async engine for the database.

    :param DB database: Postgres database credentials
    :return AsyncEngine: Async Engine 
    """

    engine = create_async_engine(
        URL(
            'postgresql+asyncpg',
            database.user,
            database.password,
            database.host,
            database.port,
            database.name,
            query={},
        ), future=True,
    )
    log.info('Connected to database')
    
    return engine
