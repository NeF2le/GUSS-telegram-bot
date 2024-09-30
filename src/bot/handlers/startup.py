from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from src.bot.handlers.menu_content import get_menu_content
from src.enums import MenuName
from src.bot.utils.callback_fabrics import MenuCallback

router = Router()


@router.message(CommandStart(), Command('start'))
async def start_bot(message: Message, state: FSMContext):
    """
    Sends a start message to user.
    :param message:
    :param state:
    :return:
    """
    await state.clear()
    text, kb = await get_menu_content(MenuCallback(level=0, menu_name=MenuName.START))

    await message.answer(text=text, reply_markup=kb, disable_web_page_preview=True)
