from aiogram.fsm.state import StatesGroup, State


class AddPerson(StatesGroup):
    vk_url = State()
    first_name = State()
    last_name = State()
    committee_name = State()


class UpdatePerson(StatesGroup):
    first_name = State()
    last_name = State()


class UpdatePersonPoints(StatesGroup):
    comment = State()


class AddEventRegistrationTable(StatesGroup):
    table_url = State()
