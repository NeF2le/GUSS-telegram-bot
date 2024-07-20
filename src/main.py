import asyncio
import logging
import sys

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from config_reader import settings
from bot.middlewares.admin_user import AdminUserMiddleware
from bot.middlewares.resources import ResourcesMiddleware
from bot.handlers import startup, commands, callback_queries


async def main():
    engine = create_async_engine(
        url=settings.database_url_asyncpg,
        echo=False
    )
    session = async_sessionmaker(bind=engine, class_=AsyncSession)

    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.outer_middleware(AdminUserMiddleware())
    dp.update.middleware(ResourcesMiddleware(session=session))

    dp.include_routers(startup.router, commands.router, callback_queries.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
