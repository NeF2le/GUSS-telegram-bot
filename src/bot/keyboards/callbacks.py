from aiogram.filters.callback_data import CallbackData
from enum import Enum


class CommitteeAction(Enum):
    SELECT = "select"
    UPDATE = "update"
    DELETE = "delete"


class Committee(CallbackData, prefix="com"):
    action: CommitteeAction
    committee: str


class CommitteeMembersPagination(CallbackData, prefix="pag"):
    action: str
    page: int
    committee: str


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    committee: str | None = None
    page: int = 1
    person_id: int | None = None
    person_committees: list[str] | None = None
    person_committee: str | None = None
