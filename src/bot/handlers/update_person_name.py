from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

from src.database.database import Database
from src.bot.utils.states import UpdatePerson
from src.bot.handlers.core import update_user_menu
from src.utils.person_name import valid_name, format_person_name

router = Router()


@router.message(UpdatePerson.first_name, F.text)
async def process_person_first_name(message: Message, state: FSMContext, db: Database):
    first_name = format_person_name(message.text)
    error_valid = ''

    await state.update_data(first_name=first_name)

    if not valid_name(first_name):
        error_valid = 'Неправильный формат имени'

    if not error_valid:
        await state.update_data(all_valid=True, error_valid=None)
        await update_user_menu(db, state, message)
    else:
        await state.update_data(error_valid=error_valid, all_valid=False)

    await update_user_menu(db, state, message)


@router.message(UpdatePerson.last_name, F.text)
async def process_person_last_name(message: Message, state: FSMContext, db: Database):
    last_name = format_person_name(message.text)
    error_valid = ''

    await state.update_data(last_name=last_name)

    if not valid_name(last_name):
        error_valid = 'Неправильный формат фамилии'

    if not error_valid:
        await state.update_data(all_valid=True, error_valid=None)
        await update_user_menu(db, state, message)
    else:
        await state.update_data(error_valid=error_valid, all_valid=False)

    await update_user_menu(db, state, message)
