from src.config_reader import settings
from src.schemas import EventRegistrationTablePersonDTO
from src.database import Database
from src.api import GoogleAPI
from src.exceptions import GoogleAPIError
from src.bot.utils import find_best_matched_person
from gspread.exceptions import SpreadsheetNotFound
from builtins import PermissionError


async def process_event_registration_table_persons(db: Database, table_id: int, event_type_id: int,
                                                   table_persons: list[EventRegistrationTablePersonDTO]):
    db_persons_full_names = await db.get_persons_full_names()
    db_table_persons = await db.get_event_registration_table_persons(table_id=table_id)
    db_table_persons_dict = {p.full_name: p for p in db_table_persons}

    to_insert = []
    to_update = []

    for table_person in table_persons:
        if not table_person.status:
            continue

        person_full_name = table_person.full_name
        matched_person_id, ratio = find_best_matched_person(person_full_name=person_full_name,
                                                            persons_full_names=db_persons_full_names)

        if matched_person_id is None or ratio < settings.PERSON_MATCH_THRESHOLD:
            if person_full_name not in db_table_persons_dict:
                to_insert.append({
                    'full_name': person_full_name,
                    'table_id': table_id,
                    'matched_person_id': None
                })
            continue

        db_table_person = db_table_persons_dict.get(person_full_name)
        if db_table_person:
            to_update.append({
                'table_person_id': db_table_person.id,
                'event_type_id': event_type_id,
                'new_matched_person_id': matched_person_id
            })
        else:
            to_insert.append({
                'full_name': person_full_name,
                'table_id': table_id,
                'matched_person_id': matched_person_id
            })

    if to_insert:
        await db.batch_insert_event_registration_table_persons(to_insert)
    if to_update:
        await db.batch_update_event_registration_table_persons(to_update)


async def process_event_registration_tables(db: Database, google_api: GoogleAPI):
    tables = await db.get_event_registration_tables()

    for table in tables:
        try:
            table_data = google_api.get_event_registration_table_data(table.table_url)
            await process_event_registration_table_persons(db=db, table_id=table.id, table_persons=table_data.persons,
                                                           event_type_id=table.event_type_id)

        except (SpreadsheetNotFound, PermissionError):
            await db.delete_event_registration_table(id=table.id)
        except GoogleAPIError:
            continue
