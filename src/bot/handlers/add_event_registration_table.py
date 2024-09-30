from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

import re

from gspread import SpreadsheetNotFound

from src.database import Database
from src.bot.utils.states import AddEventRegistrationTable
from src.bot.handlers.core import update_user_menu
from src.api import GoogleAPI
from src.exceptions import GoogleAPIError

router = Router()


@router.message(AddEventRegistrationTable.table_url, F.text)
async def process_table_url(message: Message, state: FSMContext, db: Database, google_api: GoogleAPI):
    table_url = message.text
    error_valid = ''

    await state.update_data(table_url=table_url)

    if not re.match(r'https://docs\.google\.com/spreadsheets/d/[A-Za-z0-9_-]+/edit.*', table_url):
        error_valid = 'Неверный формат ссылки'

    elif await db.check_event_registration_table_exists(table_url):
        error_valid = 'Эта таблица уже существует в ГУСС-топе'

    try:
        table = google_api.get_table_by_url(table_url)
        if not google_api.check_table_requirements(table):
            error_valid = 'Оформление таблицы не соответствует требованиям'
    except SpreadsheetNotFound:
        error_valid = 'Такой таблицы не существует'
    except PermissionError:
        error_valid = 'Нет прав доступа для просмотра таблицы'
    except GoogleAPIError:
        error_valid = 'Ошибка взаимодействия с API'

    if not error_valid:
        table_title = google_api.get_table_title(table_url)
        await state.update_data(table_title=table_title, error_valid=None, all_valid=True)
    else:
        await state.update_data(error_valid=error_valid, all_valid=False)

    await update_user_menu(db, state, message)
