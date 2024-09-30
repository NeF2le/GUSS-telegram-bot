from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from src.database.database import Database
from src.bot.utils.states import UpdatePersonPoints
from src.bot.handlers.core import update_user_menu

router = Router()


@router.message(UpdatePersonPoints.comment, F.text)
async def process_comment(message: Message, state: FSMContext, db: Database):
    comment = message.text

    await state.update_data(comment=comment)
    await update_user_menu(db, state, message)
