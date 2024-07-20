from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.database import ActionType, Base
from src.database.schemas import VkActivityDTO, PersonDTO, PersonWithPointsDTO, PersonWithPointsInCategoryDTO
from src.database.models import AuditLog, VkActivity, PersonPoints, Person
from contextlib import asynccontextmanager

from typing import Any


async def log_action(session: AsyncSession,
                     action_type: ActionType,
                     table_name: str,
                     username: str,
                     old_data: dict | None = None,
                     new_data: dict | None = None,
                     ):
    """
    Log an action in the 'audit_logs' table.
    :param session:
    :param action_type:
    :param table_name:
    :param username:
    :param old_data:
    :param new_data:
    :return:
    """
    audit_log = AuditLog(action_type=action_type,
                         table_name=table_name,
                         old_data=old_data,
                         new_data=new_data,
                         changed_by=username)
    session.add(audit_log)
    await session.commit()


@asynccontextmanager
async def insert_audito(session: AsyncSession):
    new_instances = []
    dirty_instances = []
    deleted_instances = []
    try:
        yield
        new_instances = session.new
        dirty_instances = session.dirty
        deleted_instances = session.deleted
        # await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        for instance in new_instances:
            # await match_instance_to_schema(session, instance)
            print(instance)


async def match_instance_to_schema(session: AsyncSession, instance: Base):
    if isinstance(instance, VkActivity):
        query = (
            select(VkActivity)
            .filter_by(person_id=instance.person_id, activity_id=instance.activity_id, post_id=instance.post_id)
            .options(joinedload(VkActivity.person))
            .options(joinedload(VkActivity.activity))
            .options(joinedload(VkActivity.post))
        )
        result_orm = (await session.execute(query)).unique().scalars().one()
        result_dto = VkActivityDTO.model_validate(result_orm, from_attributes=True)

        await add_audit_log(session=session,
                            action_type=ActionType.INSERT_VK_ACTIVITY,
                            table_name=VkActivity.__tablename__,
                            old_data=None,
                            new_data=result_dto.dict())

    if isinstance(instance, PersonPoints):
        query = (
            select(PersonPoints)
            .options(joinedload(PersonPoints.person).selectinload(Person.committees))
            .options(joinedload(PersonPoints.category))
            .filter_by(person_id=instance.person_id, category_id=instance.category_id)
        )
        result_orm = (await session.execute(query)).unique().scalars().one()
        result_dto = PersonWithPointsInCategoryDTO.model_validate(result_orm, from_attributes=True)

        await session.flush()
        await session.refresh(instance)

        await add_audit_log(session=session,
                            action_type=ActionType.UPDATE_PERSON_POINTS,
                            table_name=VkActivity.__tablename__,
                            old_data=None,
                            new_data=result_dto.dict())
