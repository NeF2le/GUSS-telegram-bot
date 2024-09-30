import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.client.bot import DefaultBotProperties

from logging_ import logger
from config_reader import settings
from bot.custom_dispatcher import CustomDispatcher
from bot.ui_commands import set_bot_commands
from bot.middlewares import AdminUserMiddleware, ResourcesMiddleware, LogAllEventsMiddleware
from bot import handlers, callbacks
from src.api import VkAPI, GoogleAPI, TelegraphAPI
from src.vk_activities_checker import VkActivitiesChecker
from src.database import Database


async def main():
    engine = create_async_engine(url=settings.database_url_asyncpg, echo=False)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession)
    db = Database(async_session)
    vk_api = VkAPI(settings.VK_TOKEN.get_secret_value())
    google_api = GoogleAPI(settings.google_creds_path)
    telegraph_api = TelegraphAPI()
    vk_activities_checker = VkActivitiesChecker(db=db, vk_api=vk_api)

    bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = CustomDispatcher()

    log_all_middleware = LogAllEventsMiddleware()
    dp.message.middleware(log_all_middleware)
    dp.callback_query.middleware(log_all_middleware)
    dp.update.outer_middleware(AdminUserMiddleware())
    dp.update.middleware(ResourcesMiddleware(db=db, vk_api=vk_api, google_api=google_api, telegraph_api=telegraph_api,
                                             vk_activities_checker=vk_activities_checker))

    dp.include_routers(
        handlers.startup.router,
        handlers.add_person.router,
        callbacks.guss_top_stats.router,
        callbacks.menu.router,
        handlers.update_person_name.router,
        handlers.comment_for_update_points.router,
        callbacks.action_logs.router,
        handlers.add_event_registration_table.router,
        handlers.vk_activities_check.router
    )

    await set_bot_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped!")
