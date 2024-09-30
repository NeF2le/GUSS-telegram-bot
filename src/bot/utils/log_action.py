from typing import Any
from contextlib import asynccontextmanager

from src.schemas import PersonDTO
from src.database import Database
from src.enums import ActionType


class ContextData:
    def __init__(self, person_id: int | None = None, comment: str | None = None):
        self.person_id = person_id
        self.comment = comment


async def create_action_data(db: Database, person_id: int) -> dict[str, Any]:
    person = await db.get_person(id=person_id, join_committees=True, join_points=True)
    action_data = PersonDTO.from_orm(person).model_dump(mode='json')
    return action_data


@asynccontextmanager
async def log_action(db: Database, action_type: ActionType, username: str, context_data: ContextData):
    try:
        old_data = None
        new_data = None

        if context_data.person_id:
            old_data = await create_action_data(db, context_data.person_id)
        yield
        if context_data.person_id:
            new_data = await create_action_data(db, context_data.person_id)
        await db.insert_audit_log(
            action_type=action_type.name,
            username=username,
            person_id=context_data.person_id,
            old_data=old_data,
            new_data=new_data,
            comment=context_data.comment,
        )
    except Exception as e:
        await db.rollback()
        raise e
