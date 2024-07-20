from sqlalchemy import event, select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, load_only
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError

from src.database.database import async_session, async_engine, Base, ActionType
from src.database.models import Person, Post, Committee, Activity, Category, AuditLog, PersonPoints, VkActivity, \
    CommitteeMembership
from src.database.schemas import PersonDTO, PersonWithPointsDTO, PersonWithPointsInCategoryDTO, CategoryWithPointsDTO
# from src.constants import COMMITTEE_NAMES
from .orm_utils import log_action
from src.context import current_user
from pprint import pprint


class AsyncORM:

    @staticmethod
    async def insert_membership(person_first_name: str, person_last_name: str, committee_name: str):
        """
        Insert a record in the 'committee_membership' table.
        :param person_first_name:
        :param person_last_name:
        :param committee_name:
        :return:
        """
        async with async_session() as session:
            person_query = select(Person).filter_by(first_name=person_first_name, last_name=person_last_name)
            committee_query = select(Committee).filter_by(name=committee_name)

            person = (await session.execute(person_query)).scalars().one_or_none()
            committee = (await session.execute(committee_query)).scalars().one_or_none()

            if not person or not committee:
                raise NoResultFound(
                    f"Person {person_first_name + person_last_name} or Committee {committee_name} not found"
                )

            person.committees.append(committee)
            await session.commit()

            username = current_user.get()
            if username:
                await session.refresh(person)
                new_data = PersonDTO.model_validate(person, from_attributes=True).dict()
                await log_action(session=session,
                                 action_type=ActionType.INSERT_MEMBERSHIP,
                                 table_name=CommitteeMembership.__tablename__,
                                 username=username,
                                 old_data=None,
                                 new_data=new_data)

    @staticmethod
    async def select_audit_logs():
        async with async_session() as session:
            result = (await session.execute(select(AuditLog))).scalars().all()
            pprint(result)

    @staticmethod
    async def update_membership(person_first_name: str, person_last_name: str, old_committee_name: str,
                                new_committee_name: str):
        """
        Update the person’s committee.
        :param person_first_name:
        :param person_last_name:
        :param old_committee_name:
        :param new_committee_name:
        :return:
        """
        async with async_session() as session:
            person_query = select(Person).filter_by(first_name=person_first_name, last_name=person_last_name)
            old_committee_query = select(Committee).filter_by(name=old_committee_name)
            new_committee_query = select(Committee).filter_by(name=new_committee_name)

            person = (await session.execute(person_query)).scalars().one_or_none()
            old_committee = (await session.execute(old_committee_query)).scalars().one_or_none()
            new_committee = (await session.execute(new_committee_query)).scalars().one_or_none()

            if not person or not old_committee or not new_committee:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' "
                                    f"or one of Committees '{old_committee_name, new_committee_name}' not found")

            person.committees.remove(old_committee)
            person.committees.append(new_committee)
            old_data = PersonDTO.model_validate(person, from_attributes=True).dict()
            await session.commit()

            username = current_user.get()
            if username:

                await session.refresh(person)
                new_data = PersonDTO.model_validate(person, from_attributes=True).dict()
                await log_action(session=session,
                                 action_type=ActionType.INSERT_MEMBERSHIP,
                                 table_name=CommitteeMembership.__tablename__,
                                 username=username,
                                 old_data=old_data,
                                 new_data=new_data)

    @staticmethod
    async def delete_membership(person_first_name: str, person_last_name: str, committee_name: str):
        """
        Delete the committee from the person.
        :param person_first_name:
        :param person_last_name:
        :param committee_name:
        :return:
        """
        async with async_session() as session:
            try:
                person_query = select(Person).filter_by(first_name=person_first_name, last_name=person_last_name)
                committee_query = select(Committee).filter_by(name=committee_name)

                person = (await session.execute(person_query)).scalars().one()
                committee = (await session.execute(committee_query)).scalars().one()

                if len(person.committees) > 1 and committee in person.committees:
                    person.committees.remove(committee)
                    await session.commit()
                else:
                    raise ValueError(f"Person '{person_first_name + person_last_name}' "
                                     f"hasn't Committee '{committee_name}' or has it only one")
            except NoResultFound:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' "
                                    f"or Committee '{committee_name}' not found")

    @staticmethod
    async def insert_person(person_first_name: str, person_last_name: str, vk_id: int):
        """
        Insert the person in the database.
        :param person_first_name:
        :param person_last_name:
        :param vk_id:
        :return:
        """
        async with async_session() as session:
            try:
                person = Person(first_name=person_first_name, last_name=person_last_name, vk_id=vk_id)
                session.add(person)
                await session.commit()
            except IntegrityError:
                raise UniqueViolationError(f"Person '{person_first_name + person_last_name}' "
                                           f"with vk_id={vk_id} is already exists")

    @staticmethod
    async def delete_person(person_first_name: str, person_last_name: str):
        """
        Delete the person from the database.
        :param person_first_name:
        :param person_last_name:
        :return:
        """
        async with async_session() as session:
            try:
                person_query = select(Person).filter_by(first_name=person_first_name, last_name=person_last_name)
                person = (await session.execute(person_query)).scalars().one()

                query = delete(Person).filter_by(id=person.id)
                await session.execute(query)
            except NoResultFound:
                raise NoResultFound(f"Person {person_first_name + person_last_name} doesn't exist")

    @staticmethod
    async def update_person_points(person_first_name: str, person_last_name: str, category_name: str, value: int):
        """
        Update person's points in the category.
        :param person_first_name:
        :param person_last_name:
        :param category_name:
        :param value:
        :return:
        """
        async with async_session() as session:
            try:
                person_id_subquery = (
                    select(Person.id)
                    .filter_by(first_name=person_first_name, last_name=person_last_name)
                    .scalar_subquery()
                )
                category_id_subquery = (
                    select(Category.id)
                    .filter_by(name=category_name)
                    .scalar_subquery()
                )
                query = (
                    select(PersonPoints)
                    .options(joinedload(PersonPoints.person).selectinload(Person.committees))
                    .options(joinedload(PersonPoints.category))
                    .filter_by(person_id=person_id_subquery, category_id=category_id_subquery)
                )
                person_points = (await session.execute(query)).unique().scalars().one()

                person_points.points_value += value
                await session.flush()
                await session.refresh(person_points)
                if person_points.points_value < 0:
                    person_points.points_value = 0
                await session.commit()
            except NoResultFound:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' "
                                    f"or Category '{category_name}' doesn't exist")

    @staticmethod
    async def get_person_points(person_first_name: str, person_last_name: str) -> dict[str, int]:
        """
        Return the person's points in each category.
        :param person_first_name:
        :param person_last_name:
        :return:
        """
        async with async_session() as session:
            person_id_subquery = (
                select(Person.id)
                .filter_by(first_name=person_first_name, last_name=person_last_name)
                .scalar_subquery()
            )
            query = (
                select(PersonPoints)
                .filter_by(person_id=person_id_subquery)
                .options(joinedload(PersonPoints.category))
            )
            person_points = (await session.execute(query)).unique().scalars().all()
            if not person_points:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' doesn't exist")

            result = {}
            for p in person_points:
                category_with_value = CategoryWithPointsDTO.model_validate(p, from_attributes=True).dict()
                result[category_with_value['category']['name']] = category_with_value['points_value']
            return result

    @staticmethod
    async def get_person_points_by_category(person_first_name: str, person_last_name: str, category_name: str) -> int:
        """
        Return the person's points in the certain category.
        :param person_first_name:
        :param person_last_name:
        :param category_name:
        :return:
        """
        async with async_session() as session:
            try:
                person_id_subquery = (
                    select(Person.id)
                    .filter_by(first_name=person_first_name, last_name=person_last_name)
                    .scalar_subquery()
                )
                category_id_subquery = (
                    select(Category.id)
                    .filter_by(name=category_name)
                    .scalar_subquery()
                )
                query = (
                    select(PersonPoints)
                    .options(joinedload(PersonPoints.person))
                    .options(joinedload(PersonPoints.category))
                    .filter_by(person_id=person_id_subquery, category_id=category_id_subquery)
                )
                points_value = (await session.execute(query)).scalars().one()
                return points_value
            except NoResultFound:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' "
                                    f"or Category '{category_name}' doesn't exist")

    @staticmethod
    async def get_persons_in_committee(committee_name: str) -> list[str]:
        """
        Return committee's persons.
        :param committee_name:
        :return:
        """
        async with async_session() as session:
            try:
                query = (
                    select(Committee)
                    .options(selectinload(Committee.persons))
                    .filter_by(name=committee_name)
                )
                committee = (await session.execute(query)).scalars().one()
                person_names = [person.name for person in committee.persons]
                return person_names
            except NoResultFound:
                raise NoResultFound(f"Committee '{committee_name}' doesn't exist")

    @staticmethod
    async def get_person_committees(person_first_name: str, person_last_name: str) -> list[str]:
        """
        Return the person's committees.
        :param person_first_name:
        :param person_last_name:
        :return:
        """
        async with async_session() as session:
            try:
                query = (
                    select(Person)
                    .options(selectinload(Person.committees))
                    .filter_by(first_name=person_first_name, last_name=person_last_name)
                )
                person = (await session.execute(query)).scalars().one()
                committee_names = [committee.name for committee in person.committees]
                return committee_names
            except NoResultFound:
                raise NoResultFound(f"Person '{person_first_name + person_last_name}' doesn't exist")

    @staticmethod
    async def get_activity_id_by_name(activity_name: str) -> int:
        """
        Return the activity ID by its name.
        :param activity_name:
        :return:
        """
        async with async_session() as session:
            try:
                query = select(Activity.id).filter_by(name=activity_name)
                result = (await session.execute(query)).scalars().one()
                return result
            except NoResultFound:
                raise NoResultFound(f"No result found for activity_name: {activity_name}")

    @staticmethod
    async def get_post_id_by_url(post_url: str) -> int:
        """
        Return the post ID by its url.
        :param post_url:
        :return:
        """
        async with async_session() as session:
            query = select(Post.id).filter_by(url=post_url)
            result = (await session.execute(query)).scalars().one_or_none()
            if not result:
                raise NoResultFound(f"No result found for post_url: {post_url}")
            return result

    @staticmethod
    async def get_person_id_by_name(person_first_name: str, person_last_name: str) -> int:
        """
        Return the person ID by its name.
        :param person_first_name:
        :param person_last_name:
        :return:
        """
        async with async_session() as session:
            query = select(Person.id).filter_by(first_name=person_first_name, last_name=person_last_name)
            result = (await session.execute(query)).scalars().one_or_none()
            if not result:
                raise NoResultFound(f"No result found for person_name: {person_first_name + person_last_name}")
            return result

    @staticmethod
    async def get_person_id_by_vk_id(vk_id: int) -> int:
        """
        Return the person ID by its 'vk_id'.
        :param vk_id:
        :return:
        """
        async with async_session() as session:
            query = select(Person.id).filter_by(vk_id=vk_id)
            result = (await session.execute(query)).scalars().one_or_none()
            if not result:
                raise NoResultFound(f"No result found for vk_id: {vk_id}")
            return result

    @staticmethod
    async def get_match_vk_ids_from_vk_activities(post_id: int, person_vk_ids: list[int]) -> list[int]:
        """
        Return 'vk_id' of the existing people in the 'vk_activities' table.
        :param post_id:
        :param person_vk_ids:
        :return:
        """
        async with async_session() as session:
            query = (
                select(Person.vk_id)
                .join(VkActivity, VkActivity.person_id == Person.id)
                .where(
                    and_(
                        VkActivity.post_id == post_id,
                        Person.vk_id.in_(person_vk_ids)
                    )
                )
            )
            result = (await session.execute(query)).scalars().all()
            return result if result else []

    @staticmethod
    async def insert_vk_activities(post_id: int, vk_ids: set[int], activity_id: int):
        """
        Insert data in 'vk_activities' table.
        :param post_id:
        :param vk_ids:
        :param activity_id:
        :return:
        """
        async with async_session() as session:
            async with audit_logging(session):
                new_vk_activities = []
                for vk_id in vk_ids:
                    person_id = await AsyncORM.get_person_id_by_vk_id(vk_id)
                    vk_activity = VkActivity(person_id=person_id, activity_id=activity_id, post_id=post_id)
                    new_vk_activities.append(vk_activity)

                session.add_all(new_vk_activities)

    @staticmethod
    async def update_vk_activities(post_url: str, liked_person_vk_ids: list[int],
                                   commented_person_vk_ids: list[int]):
        """
        Update 'vk_activities' table with missing records.
        :param post_url:
        :param liked_person_vk_ids:
        :param commented_person_vk_ids:
        :return:
        """
        async with async_session() as session:
            vk_like_id = await AsyncORM.get_activity_id_by_name('vk_like')
            vk_comment_id = await AsyncORM.get_activity_id_by_name('vk_comment')
            post_id = await AsyncORM.get_post_id_by_url(post_url)

            existing_liked_person_vk_ids = await AsyncORM.get_match_vk_ids_from_vk_activities(post_id,
                                                                                              liked_person_vk_ids)
            existing_commented_person_vk_ids = await AsyncORM.get_match_vk_ids_from_vk_activities(post_id,
                                                                                                  commented_person_vk_ids)

            missing_liked_person_vk_ids = set(liked_person_vk_ids) - set(existing_liked_person_vk_ids)
            missing_commented_person_vk_ids = set(commented_person_vk_ids) - set(existing_commented_person_vk_ids)

            await AsyncORM.insert_vk_activities(post_id, missing_liked_person_vk_ids, vk_like_id)
            await AsyncORM.insert_vk_activities(post_id, missing_commented_person_vk_ids, vk_comment_id)

            await session.flush()
            await session.commit()

    @staticmethod
    async def select_person_points():
        async with async_session() as session:
            query = (
                select(PersonPoints)
                .options(joinedload(PersonPoints.person))
                .options(joinedload(PersonPoints.category))
            )
            result_orm = (await session.execute(query)).unique().scalars().all()
            # result_dto = [PersonWithPointsInCategoryDTO.model_validate(inst, from_attributes=True) for inst in
            #               result_orm]
            # print(result_dto)
