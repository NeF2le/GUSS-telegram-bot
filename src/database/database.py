from datetime import datetime, date
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, desc, asc, update
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.dialects.postgresql import insert

from . import EventType
from .models import Committee, Category, VkActivity, Person, PersonPoints, Protocol, ProtocolPerson, AuditLog, \
    EventRegistrationTablePerson, EventRegistrationTable
from src.enums import ActivityType, DocumentType
from src.config_reader import settings


class Database:
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        """
        Initializes a Database instance with the provided session factory.
        :param session_factory: A function that returns a new asynchronous database session.
        """
        self.session_factory = session_factory

    async def rollback(self):
        async with self.session_factory() as session:
            await session.rollback()

    async def check_person_exists(self, **kwargs: Any) -> bool:
        person = await self.get_person(**kwargs)
        return person is not None

    async def check_membership(self, committee_id: int, person_id: int) -> bool:
        person = await self.get_person(id=person_id, join_committees=True)
        if not person:
            return False
        for committee in person.committees:
            if committee.id == committee_id:
                return True
        return False

    async def check_event_registration_table_exists(self, table_url: str) -> bool:
        table = await self.get_event_registration_table(table_url=table_url)
        return table is not None

    async def check_all_points_added(self, document_type: DocumentType, document_id: int) -> bool:
        async with self.session_factory() as session:
            if document_type == DocumentType.PROTOCOL:
                query = select(ProtocolPerson).filter_by(protocol_id=document_id, points_added=False)
            elif document_type == DocumentType.EVENT_REGISTRATION_TABLE:
                query = select(EventRegistrationTablePerson).filter_by(table_id=document_id, points_added=False)

            return (await session.execute(query)).fetchall() == 0

    async def insert_person(self, first_name: str, last_name: str, vk_id: int) -> int:
        """
        Inserts a new person into the database.
        :param first_name: The first name of the person.
        :param last_name: The last name of the person.
        :param vk_id: The unique identifier of the person in the VK.
        :return: The newly created person object.
        """
        async with self.session_factory() as session:
            try:
                person = Person(first_name=first_name, last_name=last_name, vk_id=vk_id)
                session.add(person)
                await session.commit()
                await session.refresh(person)
                return person.id
            except IntegrityError:
                raise

    async def insert_event_registration_table(self, title: str, table_url: str,
                                              event_type_id: int) -> EventRegistrationTable:
        async with self.session_factory() as session:
            try:
                table = EventRegistrationTable(title=title, table_url=table_url, event_type_id=event_type_id)
                session.add(table)
                await session.commit()
                await session.refresh(table)
                return table
            except IntegrityError:
                raise

    async def insert_event_registration_table_person(self, full_name: str, table_id: int,
                                                     matched_person_id: int | None = None):
        async with self.session_factory() as session:
            try:
                table_person = EventRegistrationTablePerson(table_id=table_id, full_name=full_name,
                                                            matched_person_id=matched_person_id)
                session.add(table_person)
                await session.commit()
            except IntegrityError:
                return

    async def insert_person_points(self, person_id: int):
        """
        Inserts a new set of person points for all categories in the database for a given person.
        :param person_id: The ID of the person for whom the person points to be inserted.
        :return: None.
        """
        async with self.session_factory() as session:
            categories = await self.get_categories()
            for category in categories:
                pp = PersonPoints(person_id=person_id, category_id=category.id)
                session.add(pp)
            await session.flush()
            await session.commit()

    async def insert_protocol(self, protocol_number: int, protocol_date: date,
                              committee_id: int) -> Protocol | None:
        async with self.session_factory() as session:
            try:
                new_protocol = Protocol(number=protocol_number, date=protocol_date, committee_id=committee_id)
                session.add(new_protocol)
                await session.commit()
                await session.refresh(new_protocol)
                return new_protocol
            except IntegrityError:
                raise

    async def insert_protocol_person(self, protocol_id: int, full_name: str, matched_person_id: int | None = None):
        async with self.session_factory() as session:
            try:
                protocol_person = ProtocolPerson(full_name=full_name, matched_person_id=matched_person_id,
                                                 protocol_id=protocol_id)
                session.add(protocol_person)
                await session.commit()
            except IntegrityError:
                return

    async def insert_membership(self, person_id: int, committee_id: int):
        """
        Inserts a new membership record in the database, associating a person with a committee.
        :param person_id: The ID of the person to be associated with the committee.
        :param committee_id: The ID of the committee to which the person will be associated.
        :return: None.
        """
        async with self.session_factory() as session:
            person = await self.get_person(id=person_id, join_committees=True)
            committee = await self.get_committee(id=committee_id)
            if not person or not committee:
                raise NoResultFound(
                    f"Person '{person.first_name} {person.last_name}' or Committee '{committee.name}' not found"
                )
            person.committees.append(committee)
            await session.merge(person)
            await session.commit()

    async def insert_vk_activity(self, person_id: int, post_url: str, activity_type: ActivityType) -> bool:
        """
        Inserts a new VK activity record into the database.
        :param person_id: The ID of the person associated with the VK activity.
        :param post_url: The URL of the VK post related to the activity.
        :param activity_type: The type of VK activity.
        :return: True if OK else False.
        """
        async with self.session_factory() as session:
            try:
                vk_activity = VkActivity(person_id=person_id, post_url=post_url, activity_type=activity_type)
                session.add(vk_activity)
                await session.commit()
                return True
            except IntegrityError:
                await session.rollback()
                return False

    async def insert_audit_log(self, action_type: str, username: str, person_id: int | None = None,
                               old_data: dict | None = None, new_data: dict | None = None, comment: str | None = None):
        """
        Inserts a new audit log record into the database.
        :param action_type: The type of action being logged.
        :param username: The username of the person performing the action.
        :param person_id: The ID of the person associated with the action. Defaults to None.
        :param old_data: The old data before the action. Defaults to None.
        :param new_data: The new data after the action. Defaults to None.
        :param comment: Additional comments about the action. Defaults to None.
        :return: None.
        """
        async with self.session_factory() as session:
            audit_log = AuditLog(action_type=action_type, person_id=person_id, changed_by=username, old_data=old_data,
                                 new_data=new_data, comment=comment)
            session.add(audit_log)
            await session.commit()

    async def get_protocol_numbers(self, committee_id: int) -> list[int]:
        async with self.session_factory() as session:
            result = await session.execute(select(Protocol.number).filter_by(committee_id=committee_id))
            protocol_numbers = result.scalars().all()
            return list(protocol_numbers)

    async def get_protocols(self, committee_id: int) -> list[Protocol]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Protocol).filter_by(committee_id=committee_id).order_by(asc(Protocol.number)))
            protocols = result.scalars().all()
            return list(protocols)

    async def get_vk_activities(self) -> list[dict[str, Any]]:
        """
        Retrieves a list of all VK activities from the database.
        :return: A list of VkActivity objects retrieved from the database.
        """
        async with self.session_factory() as session:
            result = await session.execute(select(VkActivity))
            vk_activities = result.scalars().all()
            vk_activities_data = [{
                'person_id': activity.person_id,
                'post_url': activity.post_url,
                'activity_type': activity.activity_type
            } for activity in vk_activities]

            return vk_activities_data

    async def get_persons(self) -> list[Person]:
        """
        Retrieves a list of all persons from the database.
        :return: A list of Person objects retrieved from the database.
        """
        async with self.session_factory() as session:
            result = await session.execute(select(Person))
            persons = result.scalars().all()
            return list(persons)

    async def get_committees(self, join_persons: bool = False, join_person_points: bool = False) -> list[Committee]:
        """
        Retrieves a list of all committees from the database.
        :param join_persons: If True, includes associated persons in the query. Defaults to False.
        :param join_person_points: If True, includes associated person points in the query. Defaults to False.
        :return: A list of Committee objects retrieved from the database.
        """
        async with self.session_factory() as session:
            query = select(Committee)
            if join_persons:
                person_query = selectinload(Committee.persons)
                if join_person_points:
                    person_query = person_query.options(
                        selectinload(Person.points).joinedload(PersonPoints.category)
                    )
                query = query.options(person_query)

            result = await session.execute(query)
            committees = result.unique().scalars().all()
            return list(committees)

    async def get_categories(self) -> list[Category]:
        """
        Retrieves a list of all categories from the database.
        :return: A list of Category objects retrieved from the database.
        """
        async with self.session_factory() as session:
            result = await session.execute(select(Category).options(selectinload(Category.persons_points)))
            categories = result.scalars().all()
            return list(categories)

    async def get_event_registration_tables(self) -> list[EventRegistrationTable]:
        async with self.session_factory() as session:
            result = await session.execute(select(EventRegistrationTable))
            tables = result.scalars().all()
            return list(tables)

    async def get_event_registration_table_title(self, **kwargs: Any) -> str:
        async with self.session_factory() as session:
            query = select(EventRegistrationTable.title).filter_by(**kwargs)
            table_title = (await session.execute(query)).scalar_one_or_none()
            if not table_title:
                raise NoResultFound(f"Event Registration Table not found with provided arguments")
            return table_title

    async def get_committee_protocols(self, committee_id: int) -> list[Protocol]:
        """
        Retrieves a list of protocols associated with a specific committee from the database.
        :param committee_id: The ID of the committee.
        :return: A list of Protocol objects associated with the specified committee.
        """
        async with self.session_factory() as session:
            query = (select(Protocol).filter_by(committee_id=committee_id))
            protocols = (await session.execute(query)).scalars().all()
            return list(protocols)

    async def get_committee_members(self, committee_id: int) -> list[Person]:
        """
        Retrieves a list of members associated with a specific committee from the database.
        :param committee_id: The ID of the committee.
        :return: A list of Person objects associated with the specific committee.
        """
        async with self.session_factory() as session:
            query = (
                select(Committee)
                .options(selectinload(Committee.persons))
                .filter_by(id=committee_id)
            )
            committee = (await session.execute(query)).scalars().one_or_none()
            if not committee:
                raise NoResultFound(f"Committee '{committee.name}' not found")
            return committee.persons

    async def get_persons_full_names(self) -> dict[int, str]:
        async with self.session_factory() as session:
            result = await session.execute(select(Person.id, Person.first_name, Person.last_name))
            rows = result.fetchall()
            return {row.id: f"{row.first_name} {row.last_name}" for row in rows}

    async def get_persons_ids_and_vk_ids(self) -> list[dict[str, Any]]:
        async with self.session_factory() as session:
            result = await session.execute(select(Person.id, Person.vk_id))
            rows = result.fetchall()
            return [{"person_id": row.id, "vk_id": row.vk_id} for row in rows]

    async def get_person(self, join_committees: bool = False, join_points: bool = False,
                         **kwargs: Any) -> Person | None:
        """
        Retrieves a person from the database based on the provided keyword arguments.
        :param join_points:
        :param join_committees:
        :param kwargs: Keyword arguments to filter the person. The keys should match the column names in the Person model.
        :return: The Person object that matches the provided kwargs, or None if no match is found.
            The Person object includes associated committees and person points, with their respective categories.
        """
        async with self.session_factory() as session:
            query = select(Person).filter_by(**kwargs)
            if join_committees:
                query = query.options(selectinload(Person.committees))
            if join_points:
                query = query.options(selectinload(Person.points).joinedload(PersonPoints.category))
            person = (await session.execute(query)).unique().scalars().one_or_none()
            return person

    async def get_person_id(self, **kwargs: Any) -> int | None:
        async with self.session_factory() as session:
            query = select(Person.id).filter_by(**kwargs)
            person_id = (await session.execute(query)).scalars().one_or_none()
            return person_id

    async def get_event_registration_table(self, join_persons: bool = False,
                                           **kwargs: Any) -> EventRegistrationTable | None:
        async with self.session_factory() as session:
            query = select(EventRegistrationTable).filter_by(**kwargs)
            if join_persons:
                query = query.options(selectinload(EventRegistrationTable.persons))
            table = (await session.execute(query)).scalars().one_or_none()
            return table

    async def get_event_registration_table_person(self, **kwargs: Any) -> EventRegistrationTablePerson | None:
        async with self.session_factory() as session:
            query = select(EventRegistrationTablePerson).filter_by(**kwargs)
            table_person = (await session.execute(query)).scalars().one_or_none()
            return table_person

    async def get_event_registration_table_persons(self, **kwargs: Any) -> list[EventRegistrationTablePerson]:
        async with self.session_factory() as session:
            query = select(EventRegistrationTablePerson).filter_by(**kwargs)
            table_persons = (await session.execute(query)).scalars().all()
            return list(table_persons)

    async def get_committee(self, **kwargs: Any) -> Committee | None:
        """
        Retrieves a committee from the database based on the provided kwargs.
        :param kwargs: Keyword arguments to filter the committee. The keys should match the column names in the Committee model.
        :return: The Committee object that matches the provided kwargs, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(Committee).filter_by(**kwargs)
            committee = (await session.execute(query)).scalars().one_or_none()
            return committee

    async def get_committee_id(self, committee_name: str) -> int | None:
        async with self.session_factory() as session:
            query = select(Committee.id).filter_by(name=committee_name)
            committee_id = (await session.execute(query)).scalars().one_or_none()
            return committee_id

    async def get_committee_name(self, committee_id: int) -> str | None:
        """
        Retrieves the date of a specific protocol from the database.
        :param committee_id: The ID of the committee whose name needs to be retrieved.
        :return: The name of the specified committee, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(Committee.name).filter_by(id=committee_id)
            committee_name = (await session.execute(query)).scalars().one_or_none()
            return committee_name

    async def get_protocol(self, join_persons: bool = False, **kwargs: Any) -> Protocol | None:
        async with self.session_factory() as session:
            query = select(Protocol).filter_by(**kwargs)
            if join_persons:
                query = query.options(selectinload(Protocol.persons))
            protocol = (await session.execute(query)).scalars().one_or_none()
            return protocol

    async def get_protocol_date(self, protocol_id: int) -> datetime | None:
        """
        Retrieves the date of a specific protocol from the database.
        :param protocol_id: The ID of the protocol whose date needs to be retrieved.
        :return: The date of the specified protocol, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(Protocol.date).filter_by(id=protocol_id)
            protocol_date = (await session.execute(query)).scalars().one_or_none()
            return protocol_date

    async def get_protocol_person(self, **kwargs: Any) -> ProtocolPerson | None:
        """
        Retrieves a protocol person from the database based on the provided kwargs.
        :param kwargs: Keyword arguments to filter the protocol person. The keys should match the column names in the ProtocolPerson model.
        :return: The ProtocolPerson object that matches the provided kwargs, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(ProtocolPerson).filter_by(**kwargs)
            protocol_person = (await session.execute(query)).scalars().one_or_none()
            return protocol_person

    async def get_protocol_persons(self, **kwargs: Any) -> list[ProtocolPerson]:
        """
        Retrieves a list of protocol persons associated with a specific protocol from the database.
        :param kwargs: Keyword arguments to filter the protocol persons. The keys should match the column names in the ProtocolPerson model.
        :return: A list of ProtocolPerson objects associated with the specified protocol.
        """
        async with self.session_factory() as session:
            query = select(ProtocolPerson).filter_by(**kwargs)
            protocol_persons = (await session.execute(query)).scalars().all()
            return list(protocol_persons)

    async def get_category(self, **kwargs) -> Category | None:
        """
        Retrieves a category from the database based on the provided kwargs.
        :param kwargs: Keyword arguments to filter the category. The keys should match the column names in the Category model.
        :return: The Category object that matches the provided kwargs, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(Category).filter_by(**kwargs)
            category = (await session.execute(query)).scalars().one_or_none()
            return category

    async def get_person_points(self, **kwargs) -> PersonPoints | None:
        """
        Retrieves a person points from the database based on the provided kwargs.
        :param kwargs: Keyword arguments to filter the person points. The keys should match the column names in the PersonPoints model.
        :return: The PersonPoints object that matches the provided kwargs, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(PersonPoints).filter_by(**kwargs)
            person_points = (await session.execute(query)).scalars().one_or_none()
            return person_points

    async def get_audit_log(self, **kwargs) -> AuditLog | None:
        """
        Retrieves an audit log from the database based on the provided kwargs.
        :param kwargs: Keyword arguments to filter the audit log. The keys should match the column names in the AuditLog model.
        :return: The AuditLog object that matches the provided kwargs, or None if no match is found.
        """
        async with self.session_factory() as session:
            query = select(AuditLog).filter_by(**kwargs)
            audit_log = (await session.execute(query)).scalars().one_or_none()
            return audit_log

    async def get_audit_logs(self, limit: int) -> list[AuditLog]:
        """
        Retrieves a list of audit logs from the database, limited by the provided limit.
        :param limit: The maximum number of audit logs to retrieve.
        :return: A list of AuditLogs objects retrieved from the database, limited by the provided limit.
        """
        async with self.session_factory() as session:
            query = select(AuditLog).order_by(desc(AuditLog.changed_at)).limit(limit)
            audit_logs = (await session.execute(query)).scalars().all()
            return list(audit_logs)

    async def delete_person(self, person_id: int):
        """
        Deletes a person from the database based on the provided ID.
        :param person_id: The ID of the person to be deleted.
        :return: None.
        """
        async with self.session_factory() as session:
            person = await self.get_person(id=person_id)
            if not person:
                return
            await session.execute(delete(Person).filter_by(id=person_id))
            await session.commit()

    async def delete_protocol(self, **kwargs: Any):
        async with self.session_factory() as session:
            protocol = await self.get_protocol(**kwargs, join_persons=True)
            if not protocol:
                return
            for person in protocol.persons:
                attendance_category = await self.get_category(name='Посещаемость')
                if person.matched_person_id:
                    await self.update_person_points(person_id=person.matched_person_id,
                                                    category_id=attendance_category.id,
                                                    points_value=-settings.COMMITTEE_ATTENDANCE_POINTS)
            await session.delete(protocol)
            await session.commit()

    async def delete_event_registration_table(self, **kwargs: Any):
        async with self.session_factory() as session:
            event_registration_table = await self.get_event_registration_table(**kwargs, join_persons=True)
            if not event_registration_table:
                return
            for person in event_registration_table.persons:
                attendance_category = await self.get_category(name='Посещаемость')
                if person.matched_person_id:
                    await self.update_person_points(person_id=person.matched_person_id,
                                                    category_id=attendance_category.id,
                                                    points_value=-settings.COMMITTEE_ATTENDANCE_POINTS)
            await session.delete(event_registration_table)
            await session.commit()

    async def batch_delete_protocol_person(self, person_ids: list[int]):
        async with self.session_factory() as session:
            query = delete(ProtocolPerson).where(ProtocolPerson.id.in_(person_ids))

            await session.execute(query)
            await session.commit()

    async def update_person_points(self, person_id: int, category_id: int, points_value: int):
        """
        Updates the points value for a specific person in a given category.
        :param person_id: The ID of the person whose points value needs to be updated.
        :param category_id: The ID of the category in which the person's value needs to be updated.
        :param points_value: The new points value to be set for the person in the specific category.
        :return: None.
        """
        async with self.session_factory() as session:
            person_points = await self.get_person_points(person_id=person_id, category_id=category_id)
            if person_points is None:
                return
            person_points.points_value += points_value
            session.add(person_points)
            await session.commit()

    async def update_person_name(self, person_id: int, new_first_name: str | None = None,
                                 new_last_name: str | None = None):
        """
        Updates the first ana/or last name of a person in the database.
        :param person_id: The ID of the person whose name needs to be updated.
        :param new_first_name: The new first name to be set for the person. If None, the first name remains unchanged.
        :param new_last_name: The new last name to be set for the person. If None, the last name remains unchanged.
        :return: None.
        """
        async with self.session_factory() as session:
            person = await self.get_person(id=person_id)
            if new_first_name:
                person.first_name = new_first_name
            if new_last_name:
                person.last_name = new_last_name
            session.add(person)
            await session.commit()

    async def update_person_committee(self, person_id: int, current_committee_id: int, new_committee_id: int):
        """
        Updates the committee association of a person in the database.
        :param person_id: The ID of the person whose committee association needs to be updated.
        :param current_committee_id: The ID of the current committee that the person is associated with.
        :param new_committee_id: The ID of the new committee to which the person needs to be associated.
        :return: None.
        """
        async with self.session_factory() as session:
            person = await self.get_person(id=person_id, join_committees=True)
            current_committee = await self.get_committee(id=current_committee_id)
            new_committee = await self.get_committee(id=new_committee_id)
            for committee in person.committees:
                if committee.id == current_committee.id:
                    person.committees.remove(committee)
                    person.committees.append(new_committee)

            await session.merge(person)
            await session.commit()

    async def batch_update_protocol_persons(self, persons_data: list[dict]):
        async with self.session_factory() as session:
            for person in persons_data:
                try:
                    protocol_person_id = person.get('id')
                    new_matched_person_id = person.get('matched_person_id')
                    protocol_person = await self.get_protocol_person(id=protocol_person_id)

                    if protocol_person.points_added:
                        # The fact that 'points_added' is True and 'matched_person_id' is None means
                        # that matched person has been deleted from the database and it doesn't need to be re-added points.
                        if not protocol_person.matched_person_id:
                            return

                        if protocol_person.matched_person_id == new_matched_person_id:
                            return

                        attendance_category = await self.get_category(name='Посещаемость')
                        await self.update_person_points(person_id=protocol_person.matched_person_id,
                                                        category_id=attendance_category.id,
                                                        points_value=-settings.COMMITTEE_ATTENDANCE_POINTS)
                        await self.update_person_points(person_id=new_matched_person_id,
                                                        category_id=attendance_category.id,
                                                        points_value=settings.COMMITTEE_ATTENDANCE_POINTS)
                    protocol_person.matched_person_id = new_matched_person_id
                    session.add(protocol_person)
                    await session.commit()
                except IntegrityError:
                    raise


    async def batch_insert_event_registration_table_persons(self, persons_data: list[dict]):
        async with self.session_factory() as session:
            try:
                query = insert(EventRegistrationTablePerson).values(persons_data).on_conflict_do_nothing()
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()

    async def batch_insert_protocol_persons(self, persons_data: list[dict]):
        async with self.session_factory() as session:
            try:
                query = insert(ProtocolPerson).values(persons_data).on_conflict_do_nothing()
                await session.execute(query)
                await session.commit()
            except IntegrityError:
                await session.rollback()

    async def batch_update_event_registration_table_persons(self, persons_data: list[dict]):
        async with self.session_factory() as session:
            try:
                for person_data in persons_data:
                    table_person_id = person_data.get('table_person_id')
                    new_matched_person_id = person_data.get('new_matched_person_id')
                    query = (
                        update(EventRegistrationTablePerson)
                        .where(EventRegistrationTablePerson.id == table_person_id)
                        .values(matched_person_id=new_matched_person_id)
                    )

                    await session.execute(query)

                    table_person = await self.get_event_registration_table_person(id=table_person_id)
                    if table_person.points_added and table_person.matched_person_id != new_matched_person_id:
                        attendance_category = await self.get_category(name='Посещаемость')
                        points_value = await self.get_event_type_points(event_type_id=person_data['event_type_id'])

                        await self.update_person_points(
                            person_id=table_person.matched_person_id,
                            category_id=attendance_category.id,
                            points_value=-points_value
                        )

                        await self.update_person_points(
                            person_id=new_matched_person_id,
                            category_id=attendance_category.id,
                            points_value=points_value
                        )

                await session.commit()
            except IntegrityError:
                await session.rollback()

    async def update_points_added_mark_in_protocol_person(self, protocol_person_id: int, mark: bool = True):
        """
        Updates the 'points_added' field in the ProtocolPerson table with the provided mark.
        :param protocol_person_id: The ID of the ProtocolPerson record to be updated.
        :param mark: The new value to be set for the 'points_added' field. Defaults to True.
        :return: None.
        """
        async with self.session_factory() as session:
            protocol_person = await self.get_protocol_person(id=protocol_person_id)
            protocol_person.points_added = mark
            session.add(protocol_person)
            await session.commit()

    async def update_points_added_mark_in_table_person(self, table_person_id: int, mark: bool = True):
        async with self.session_factory() as session:
            table_person = await self.get_event_registration_table_person(id=table_person_id)
            table_person.points_added = mark
            session.add(table_person)
            await session.commit()

    async def delete_person_committee(self, person_id: int, committee_id: int):
        """
        Deletes a person's association with a specific committee in the database.
        :param person_id: The ID of the person whose committee association needs to be updated.
        :param committee_id: The ID of the committee from which the person needs to be disassociated.
        :return: None.
        """
        async with self.session_factory() as session:
            person = await self.get_person(id=person_id, join_committees=True)
            committee = await self.get_committee(id=committee_id)
            for com in person.committees:
                if com.name == committee.name:
                    person.committees.remove(com)
            session.add(person)
            await session.commit()

    async def get_person_points_top(self, top_count: int = 3) -> dict[str, list[(str, int)]]:
        async with self.session_factory() as session:
            cte = (
                select(
                    PersonPoints.category_id.label('category_id'),
                    PersonPoints.person_id.label('person_id'),
                    PersonPoints.points_value.label('points_value'),
                    func.row_number().over(partition_by=PersonPoints.category_id,
                                           order_by=PersonPoints.points_value.desc()).label('row_num')
                )
                .order_by(PersonPoints.category_id)
            ).cte(name='top_three_persons')

            query = (
                select(
                    Category.name.label('category_name'),
                    func.concat(Person.first_name, ' ', Person.last_name).label('full_name'),
                    cte.c.points_value
                )
                .select_from(
                    cte.join(Category, Category.id == cte.c.category_id)
                    .join(Person, Person.id == cte.c.person_id)
                )
                .where(cte.c.row_num <= 3)
            )

            result = (await session.execute(query)).fetchall()
            top_persons = {}

            for row in result:
                category_name = row[0]
                full_name = row[1]
                points_value = row[2]

                if category_name not in top_persons:
                    top_persons[category_name] = []

                top_persons[category_name].append((full_name, points_value))

        return top_persons

    async def get_event_type_points(self, event_type_id: int) -> int:
        async with self.session_factory() as session:
            query = select(EventType.points).filter_by(id=event_type_id)
            points = (await session.execute(query)).fetchone()
            return points[0]

    async def get_event_types(self) -> list[EventType]:
        async with self.session_factory() as session:
            query = select(EventType).order_by(EventType.points)
            event_types = (await session.execute(query)).scalars().all()
            return list(event_types)

    async def get_event_type_name(self, event_type_id: int) -> str:
        async with self.session_factory() as session:
            query = select(EventType.name).filter_by(id=event_type_id)
            name = (await session.execute(query)).fetchone()
            return name[0]
