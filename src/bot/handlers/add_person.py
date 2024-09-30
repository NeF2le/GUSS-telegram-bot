from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.context import FSMContext

import re

from src.database import Database
from src.api import VkAPI
from src.bot.utils.states import AddPerson
from src.bot.handlers.core import update_user_menu
from src.utils.person_name import valid_name, format_person_name

router = Router()


@router.message(AddPerson.vk_url, F.text)
async def process_person_vk_url(message: Message, state: FSMContext, db: Database, vk_api: VkAPI):
    """
    Processes the 'AddPerson:first_name' state. This function is responsible for handling the VK URL input
    during the addition of a new person to the GUSSTop. It validates the input, updates the state, and sends a
    response to the user.
    :param message: The incoming message containing the user's input.
    :param state: The state of the finite state machine.
    :param db: The Database object for interacting with the database.
    :param vk_api: The VkAPI object for interacting with VK API.
    :return: None.
    """
    vk_url = message.text
    vk_id = vk_api.convert_vk_url_to_id(vk_url)
    error_valid = ''

    await state.update_data(vk_url=vk_url)

    if not re.match(r'https://vk\.com/[A-Za-z0-9_-]+', vk_url):
        error_valid = 'Неверный формат ссылки'

    elif not vk_api.check_vk_user(vk_url):
        error_valid = 'Такого пользователя не существует'

    elif await db.check_person_exists(vk_id=vk_id):
        error_valid = "Человек с таким ВК уже есть в ГУСС-топе"

    if not error_valid:
        await state.update_data(vk_id=vk_id, error_valid=None)
        await state.set_state(AddPerson.first_name)
    else:
        await state.update_data(error_valid=error_valid)

    await update_user_menu(db, state, message)


@router.message(AddPerson.first_name, F.text)
async def process_person_first_name(message: Message, state: FSMContext, db: Database):
    """
    Processes the 'AddPerson:first_name' state. This function is responsible for handling the first name input
    during the addition of a new person to the GUSSTop. It validates the input, updates the state, and sends a
    response to the user.
    :param message: The incoming message containing the user's input.
    :param state: The state of the finite state machine.
    :param db: The Database object for interacting with the database.
    :return: None.
    """
    first_name = format_person_name(message.text)
    error_valid = ''

    await state.update_data(first_name=first_name)

    if not valid_name(first_name):
        error_valid = 'Неправильный формат имени'

    if not error_valid:
        await state.update_data(error_valid=None)
        await state.set_state(AddPerson.last_name)
    else:
        await state.update_data(error_valid=error_valid)

    await update_user_menu(db, state, message)


@router.message(AddPerson.last_name, F.text)
async def process_person_last_name(message: Message, state: FSMContext, db: Database):
    """
    Processes the 'AddPerson:last_name' state. This function is responsible for handling the first name input
    during the addition of a new person to the GUSSTop. It validates the input, updates the state, and sends a
    response to the user.
    :param message: The incoming message containing the user's input.
    :param state: The state of the finite state machine.
    :param db: The Database object for interacting with the database.
    :return: None.
    """
    last_name = format_person_name(message.text)
    error_valid = ''

    await state.update_data(last_name=last_name)

    if not valid_name(last_name):
        error_valid = 'Неправильный формат фамилии'

    if not error_valid:
        await state.update_data(error_valid=None)
        await state.set_state(AddPerson.committee_name)
    else:
        await state.update_data(error_valid=error_valid)

    await update_user_menu(db, state, message)


@router.message(AddPerson.committee_name, F.text)
async def process_person_committee(message: Message, state: FSMContext, db: Database):
    """
    Processes the 'AddPerson:committee' state. This function is responsible for handling the committee input
    during the addition of a new person to the GUSSTop. It validates the input, updates the state, and sends a
    response to the user.
    :param message: The incoming message containing the user's input.
    :param state: The state of the finite state machine.
    :param db: The Database object for interacting with the database.
    :return: None.
    """
    committee_name = message.text.upper()
    committees = await db.get_committees()
    error_valid = ''

    await state.update_data(committee_name=committee_name)

    if committee_name not in [com.name for com in committees]:
        error_valid = 'Такого комитета не существует'

    if not error_valid:
        await state.update_data(all_valid=True, error_valid=None)
    else:
        await state.update_data(error_valid=error_valid, all_valid=False)

    await update_user_menu(db, state, message)
