from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from src.vk_activities_checker import VkActivitiesChecker

router = Router()


@router.message(Command('start_vk_activities_checker'))
async def start_vk_activities_checker(message: Message, vk_activities_checker: VkActivitiesChecker):
    if vk_activities_checker.task_running:
        await message.reply('Чекер уже запущен')
    else:
        vk_activities_checker.start_checking()
        await message.reply('Чекер запущен')


@router.message(Command('stop_vk_activities_checker'))
async def stop_vk_activities_checker(message: Message, vk_activities_checker: VkActivitiesChecker):
    if not vk_activities_checker.task_running:
        await message.reply('Чекер не запущен')
    else:
        vk_activities_checker.stop_checking()
        await message.reply('Чекер остановлен')
