from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="start_vk_activities_checker", description="Запустить проверку активностей ВК"),
        BotCommand(command="stop_vk_activities_checker", description="Остановить проверку активностей ВК"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeAllPrivateChats())
