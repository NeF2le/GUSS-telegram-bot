import asyncio
from typing import Any

import pandas as pd
from pandas import DataFrame

from src.config_reader import settings
from src.enums import ActivityType, ActionType
from src.bot.utils import log_action, ContextData
from src.api import VkAPI
from src.database import Database
from src.logging_ import logger


class VkActivitiesChecker:
    def __init__(self, db: Database, vk_api: VkAPI):
        self.task_running = False
        self._loop = asyncio.new_event_loop()
        self.db = db
        self.vk_api = vk_api

    async def process_groups(self):
        while self.task_running:
            tasks = [self.check_activities(domain) for domain in settings.VK_GROUP_DOMAINS]
            await asyncio.gather(*tasks)
            await asyncio.sleep(settings.VK_ACTIVITIES_CHECKER_TIMEOUT)
            logger.info('VkActivityChecker has successfully iterated')

    async def check_activities(self, domain: str | int):
        activities = await self.process_group(domain)

        # Create a DataFrame and drop duplicates because a one person can only have one activity under a post
        activities_df = pd.DataFrame(activities).drop_duplicates(subset=['vk_id', 'post_url', 'activity_type'])

        persons = await self.db.get_persons_ids_and_vk_ids()
        persons_df = pd.DataFrame(persons)

        merged_df = pd.merge(activities_df, persons_df, on='vk_id', how='inner').drop(columns='vk_id')
        promotion_category = await self.db.get_category(name='Пиар ГУСС')

        await self.process_new_records(merged_df, promotion_category.id)

    async def process_new_records(self, new_records: DataFrame, promotion_category_id: int):
        for _, row in new_records.iterrows():
            person_id = row['person_id']
            post_url = row['post_url']
            activity_type = row['activity_type']
            context_data = ContextData(person_id=person_id, comment=f'Лайк поста в ВК. Ссылка {post_url}')

            try:
                await self.db.insert_vk_activity(person_id, post_url, activity_type)

                if activity_type == ActivityType.VK_LIKE:
                    context_data.comment = f'Лайк поста в ВК. Ссылка {post_url}'
                    async with log_action(db=self.db, action_type=ActionType.UPDATE_PERSON_POINTS, username='ГУСС-топ',
                                          context_data=context_data):
                        await self.db.update_person_points(person_id, promotion_category_id, settings.VK_LIKE_POINTS)
                else:
                    context_data.comment = f'Комментирование поста в ВК. Ссылка {post_url}'
                    async with log_action(db=self.db, action_type=ActionType.UPDATE_PERSON_POINTS, username='ГУСС-топ',
                                          context_data=context_data):
                        await self.db.update_person_points(person_id, promotion_category_id, settings.VK_COMMENT_POINTS)
            except Exception as e:
                logger.error(f"Ошибка при обновлении активности пользователя {person_id} по посту {post_url}: {e}")

    async def process_group(self, domain: str | int) -> list[dict[str, Any]]:
        group_data = []
        try:
            group_id = self.vk_api.get_group_id(domain)
            group_screen_name = self.vk_api.get_group_screen_name(domain)
            post_ids = self.vk_api.get_group_posts_ids(group_screen_name, count=settings.VK_GROUP_POSTS_COUNT)

            for post_id in post_ids:
                post_url = self.vk_api.get_post_url(owner_id=-group_id, post_id=post_id)

                liked_ids = self.vk_api.get_post_liked_ids(owner_id=-group_id, item_id=post_id)
                commented_ids = self.vk_api.get_post_commented_ids(owner_id=-group_id, post_id=post_id)

                for user_id in set(liked_ids + commented_ids):
                    if user_id in liked_ids:
                        activity_type = ActivityType.VK_LIKE
                        group_data.append({
                            'vk_id': user_id,
                            'post_url': post_url,
                            'activity_type': activity_type.name
                        })
                    if user_id in commented_ids:
                        activity_type = ActivityType.VK_COMMENT
                        group_data.append({
                            'vk_id': user_id,
                            'post_url': post_url,
                            'activity_type': activity_type.name
                        })

            return group_data
        except Exception as e:
            logger.error(f"Error while processing group '{domain}': {e}")

        return group_data

    def start_checking(self):
        if not self.task_running:
            self.task_running = True
            asyncio.create_task(self.process_groups())
            logger.info("VKActivityChecker has been started")

    def stop_checking(self):
        if self.task_running:
            self.task_running = False
            logger.info('VKActivityChecker has been stopped')

    def shutdown(self):
        self._loop.stop()
