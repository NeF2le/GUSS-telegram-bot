from src.api import GoogleAPI
from src.schemas import ProtocolPersonDTO
from src.config_reader import settings
from src.database import Database
from src.bot.utils import find_best_matched_person


async def process_protocol_persons(db: Database, protocol_id: int, protocol_persons: list[ProtocolPersonDTO],
                                   committee_id: int):
    db_protocol_persons = await db.get_protocol_persons(protocol_id=protocol_id)
    protocol_persons_full_names = {i: person.full_name for i, person in enumerate(protocol_persons)}
    db_protocol_persons_full_names = {person.id: person.full_name for person in db_protocol_persons}
    db_persons_full_names = await db.get_persons_full_names()

    to_insert = []
    to_update = []
    to_delete = []

    for person in db_protocol_persons:
        matched_person_id, ratio = find_best_matched_person(person_full_name=person.full_name,
                                                            persons_full_names=protocol_persons_full_names)

        # Delete protocol persons who are already in database, but aren't in the actual protocol.
        if matched_person_id is None or ratio < settings.PERSON_MATCH_THRESHOLD:
            to_delete.append(person.id)

        # Delete protocol person who are already in database, but he's full name is incomplete in the actual protocol.
        if len(protocol_persons_full_names[matched_person_id].split()) != len(person.full_name.split()):
            to_delete.append(person.id)

    for person in protocol_persons:
        # Skip a person who is already in database, but first name and last name changed.
        # 95 ratio means words changing. For example, a matching of 'Женя Корнилов' and 'Корнилов Женя' gets 95 ratio.
        matched_person_id, ratio = find_best_matched_person(person_full_name=person.full_name,
                                                            persons_full_names=db_protocol_persons_full_names)
        if matched_person_id is not None and ratio == 95:
            continue

        # Insert a person who not added in database and hasn't matched person from all persons.
        matched_person_id, ratio = find_best_matched_person(person_full_name=person.full_name,
                                                            persons_full_names=db_persons_full_names)
        membership = await db.check_membership(committee_id=committee_id, person_id=matched_person_id)
        if matched_person_id is None or not membership or ratio < settings.PERSON_MATCH_THRESHOLD:
            to_insert.append({
                'protocol_id': protocol_id,
                'full_name': person.full_name,
                'matched_person_id': None
            })
            continue

        # If a ratio of matched person is greater than 'PERSON_MATCH_THRESHOLD', it checks a person exists in database.
        # If it's true, the matched person ID will be updated.
        # If it's false, a person will be added in database with the matched person ID.
        db_protocol_person = await db.get_protocol_person(protocol_id=protocol_id, full_name=person.full_name)

        if db_protocol_person:
            to_update.append({
                'id': db_protocol_person.id,
                'matched_person_id': matched_person_id
            })
        else:
            to_insert.append({
                'full_name': person.full_name,
                'matched_person_id': matched_person_id,
                'protocol_id': protocol_id
            })

    if to_insert:
        await db.batch_insert_protocol_persons(to_insert)
    if to_update:
        await db.batch_update_protocol_persons(to_update)
    if to_delete:
        await db.batch_delete_protocol_person(to_delete)


async def process_protocols(db: Database, google_api: GoogleAPI, committee_id: int, protocol_document_id: str):
    google_doc_protocols = google_api.get_protocols_data(protocol_document_id)

    # Delete protocols which are missed in google document, but exists in database.
    google_doc_protocol_numbers = [protocol.number for protocol in google_doc_protocols]
    db_protocols_numbers = await db.get_protocol_numbers(committee_id=committee_id)
    missing_protocols_numbers = set(db_protocols_numbers) - set(google_doc_protocol_numbers)
    for number in missing_protocols_numbers:
        await db.delete_protocol(number=number, committee_id=committee_id)

    for google_doc_protocol in google_doc_protocols:
        # If protocol's fields aren't valid, then check number exists.
        # If it exists, then delete this protocol and continue loop.
        if not google_doc_protocol.is_valid():
            if google_doc_protocol.number:
                await db.delete_protocol(number=google_doc_protocol.number, committee_id=committee_id)
                continue

        db_protocol = await db.get_protocol(number=google_doc_protocol.number, committee_id=committee_id)
        protocol_number = google_doc_protocol.number
        protocol_date = google_doc_protocol.protocol_date

        # If a number of the google document protocol equals to a number of the database protocol
        # and dates are the same, then delete this protocol.
        # And insert a last protocol with this number.
        if db_protocol:
            if db_protocol.date != google_doc_protocol.protocol_date:
                await db.delete_protocol(id=db_protocol.id)
                db_protocol = await db.insert_protocol(protocol_number=protocol_number, protocol_date=protocol_date,
                                                       committee_id=committee_id)
        else:
            db_protocol = await db.insert_protocol(protocol_number=protocol_number, protocol_date=protocol_date,
                                                   committee_id=committee_id)

        await process_protocol_persons(db, db_protocol.id, google_doc_protocol.persons, committee_id)
