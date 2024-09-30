from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from typing import Callable, Any, Awaitable
from src.config_reader import settings


class AdminUserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        """
        Checks the user's ID in 'ADMIN_IDS'.
        :param handler:
        :param event:
        :param data:
        :return:
        """
        user_id = event.message.from_user.id if event.message else event.callback_query.from_user.id
        if user_id in settings.ADMIN_IDS:
            return await handler(event, data)

        await event.answer(
            text="У тебя недостаточно прав",
            show_alert=True
        )
