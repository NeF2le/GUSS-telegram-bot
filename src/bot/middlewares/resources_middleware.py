from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.vk_activities_checker import VkActivitiesChecker
from src.database.database import Database
from src.api import VkAPI, GoogleAPI, TelegraphAPI


class ResourcesMiddleware(BaseMiddleware):
    def __init__(self, db: Database, vk_api: VkAPI, google_api: GoogleAPI, telegraph_api: TelegraphAPI,
                 vk_activities_checker: VkActivitiesChecker) -> None:
        self.db = db
        self.vk_api = vk_api
        self.google_api = google_api
        self.telegraph_api = telegraph_api
        self.vk_activities_checker = vk_activities_checker

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any]
    ) -> Any:
        """
        Provides resources such as database, vk_api, google_api, telegraph_api.
        :param handler:
        :param event:
        :param data:
        :return:
        """
        data['vk_api'] = self.vk_api
        data['db'] = self.db
        data['google_api'] = self.google_api
        data['telegraph_api'] = self.telegraph_api
        data['vk_activities_checker'] = self.vk_activities_checker

        return await handler(event, data)
