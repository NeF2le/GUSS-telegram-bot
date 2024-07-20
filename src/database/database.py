from .models import Committee, CommitteeMembership, Category, VkActivity, Activity, Person, Post, PersonPoints, \
    AuditLog, Base

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError, NoResultFound
from asyncpg.exceptions import UniqueViolationError


persons_data = [
    {"first_name": "Женя", "last_name": "Корнилов", "vk_id": 987123456},
    {"first_name": "Юля", "last_name": "Лебедева", "vk_id": 853853283},
    {"first_name": "Иван", "last_name": "Немеш", "vk_id": 123456789},
    {"first_name": "Фая", "last_name": "Хватова", "vk_id": 999888777},
    {"first_name": "Ксюша", "last_name": "Шуина", "vk_id": 942860327},
    {"first_name": "Ксюша", "last_name": "Королева", "vk_id": 745932754}
]

posts_data = [
    {"url": "https://vk.com/wall-491788_6581"},
    {"url": "https://vk.com/wall-491788_6723"},
    {"url": "https://vk.com/wall-491788_6713"},
    {"url": "https://vk.com/wall-491788_6704"},
    {"url": "https://vk.com/wall-491788_6699"},
]


class Database:
    def __init__(self, session: AsyncSession) -> None:
        """
        Initializes self.
        :param session:
        """
        self.session = session

    async def insert_test_data(self):
        async with self.session as session:
            insert_persons = insert(Person).values(persons_data)
            await session.execute(insert_persons)
            await session.commit()

    async def insert_person(self, first_name: str, last_name: str, vk_id: int):
        """
        Inserts the person in the database.
        :param first_name:
        :param last_name:
        :param vk_id:
        :return:
        """
        async with self.session as session:
            try:
                person = Person(first_name=first_name, last_name=last_name, vk_id=vk_id)
                session.add(person)
                await session.commit()

                await session.refresh(person)
                return person
            except IntegrityError:
                raise

    async def insert_person_points(self, person_id: int):
        """
        Inserts the record in 'person_points' table.
        :param person_id:
        :return:
        """
        async with self.session as session:
            categories = (await session.execute(select(Category))).scalars().all()
            for category in categories:
                pp = PersonPoints(person_id=person_id, category_id=category.id)
                session.add(pp)
            await session.commit()

    async def get_committees(self) -> list[str]:
        """
        Returns a list of committees' names.
        :return:
        """
        async with self.session as session:
            result = await session.execute(select(Committee))
            committees = result.scalars().all()
            return [committee.name for committee in committees]

    async def get_committee_members(self, committee_name: str) -> list[Person]:
        """
        Returns the full name with ID of committee's members.
        :param committee_name:
        :return:
        """
        async with self.session as session:
            query = (
                select(Committee)
                .options(selectinload(Committee.persons))
                .filter_by(name=committee_name)
            )
            committee = (await session.execute(query)).scalars().one()
            if not committee:
                raise NoResultFound(f"Committee '{committee_name}' not found")

            return committee.persons

    async def add_membership(self, person_first_name: str, person_last_name: str, committee_name: str):
        """
        Adds committee membership to a person.
        :param person_first_name:
        :param person_last_name:
        :param committee_name:
        :return:
        """
        async with self.session as session:
            person_query = select(Person).filter_by(first_name=person_first_name, last_name=person_last_name)
            committee_query = select(Committee).filter_by(name=committee_name)

            person = (await session.execute(person_query)).scalars().one_or_none()
            committee = (await session.execute(committee_query)).scalars().one_or_none()

            if not person or not committee:
                raise NoResultFound(
                    f"Person '{person_first_name} {person_last_name}' or Committee '{committee_name}' not found"
                )

            person.committees.append(committee)
            await session.commit()

    async def get_person(self, person_id: int) -> Person | None:
        """
        Return 'Person' object by person ID.
        :param person_id:
        :return:
        """
        async with self.session as session:
            query = (
                select(Person)
                .filter_by(id=person_id)
                .options(selectinload(Person.committees))
                .options(selectinload(Person.points))
            )
            person = (await session.execute(query)).scalars().one_or_none()

            return person

    async def insert_person_with_relationships(self, first_name: str, last_name: str, committee_name: str):
        person = await self.insert_person(first_name, last_name)
