from aiogram.filters.callback_data import CallbackData
from src.enums import MenuName


class MenuCallback(CallbackData, prefix="menu"):
    """
    A class representing a callback data for menu navigation.
    """
    level: int
    menu_name: MenuName
    page: int = 1
    is_back_button: bool | None = None
    committee_id: int | None = None
    person_id: int | None = None
    protocol_id: int | None = None
    table_id: int | None = None
    event_type_id: int | None = None
    current_person_committee_id: int | None = None
    new_person_committee_id: int | None = None
    category_id: int | None = None
    current_points: int | None = None
    old_points: int | None = None
    edit_points: int | None = None
