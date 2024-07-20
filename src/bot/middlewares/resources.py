import logging
from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from src.database.database import Database
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ResourcesMiddleware(BaseMiddleware):
    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        """
        Initializes self.
        :param session:
        """
        self.session = session

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        """
        Provides resources such as database.
        :param handler:
        :param event:
        :param data:
        :return:
        """
        async with self.session() as session:
            db = Database(session)
            data["db"] = db
            return await handler(event, data)
