from src.bot.handlers.process_event_registration_tables import process_event_registration_tables
from src.bot.keyboards.inline import *
from src.bot.template_engine import render_template
from src.bot.utils import Paginator, MenuCallback, get_document_process_result_url
from src.bot.handlers.process_protocols import process_protocols
from src.config_reader import settings
from src.database import Database
from src.api import GoogleAPI, TelegraphAPI
from src.enums import MenuName, DocumentType


def get_pag_buttons(paginator: Paginator) -> dict[str, str]:
    """
    Generate pagination buttons based on the Paginator object.
    :param paginator: An instance of Paginator that contains information about the current page and total pages.
    :return: A dictionary containing the pagination buttons. The keys are the button emojis, and the values are the corresponding actions.
    """
    buttons = {}
    if paginator.has_previous():
        buttons["◀️"] = "prev"

    if paginator.has_next():
        buttons["▶️"] = "next"

    return buttons


def start_menu(level: int, menu_name: MenuName) -> (str, InlineKeyboardMarkup):
    """
    Returns 'start' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    text = render_template(menu_name=menu_name, action_logs_limit=settings.ACTION_LOGS_LIMIT)
    kb = get_start_kb(level)

    return text, kb


async def select_committee_menu(level: int, menu_name: MenuName, db: Database) -> (str, InlineKeyboardMarkup):
    """
    Returns 'select_committee' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    committees = await db.get_committees()
    text = render_template(menu_name=menu_name)
    kb = get_select_committee_kb(level, committees)

    return text, kb


async def committee_menu(level: int, menu_name: MenuName, db: Database, committee_id: int) -> (
        str, InlineKeyboardMarkup):
    """
    Returns 'committee' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    committee = await db.get_committee(id=committee_id)

    text = render_template(menu_name=menu_name, committee_name=committee.name, committee_talisman=committee.talisman)
    kb = get_committee_kb(level=level, committee_id=committee_id)

    return text, kb


async def committee_protocols_menu(
        level: int,
        menu_name: MenuName,
        db: Database,
        committee_id: int,
        page: int,
        google_api: GoogleAPI | None = None
) -> (str, InlineKeyboardMarkup):
    """
    Returns 'committee_protocols' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param committee_id: The ID of the committee.
    :param page: The current page number.
    :param google_api: The GoogleAPI object.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    committee = await db.get_committee(id=committee_id)

    await process_protocols(db=db, google_api=google_api, committee_id=committee_id,
                            protocol_document_id=committee.protocols_document_id)

    db_protocols = await db.get_protocols(committee_id)
    paginator = Paginator(db_protocols, page)
    protocols_on_page = paginator.get_page()
    pag_buttons = get_pag_buttons(paginator)

    text = render_template(menu_name=menu_name, committee_name=committee.name, committee_talisman=committee.talisman,
                           protocols=db_protocols)
    kb = get_committee_protocols_kb(
        level=level,
        menu_name=menu_name,
        committee_id=committee_id,
        page=page,
        protocols=protocols_on_page,
        pag_buttons=pag_buttons
    )

    return text, kb


async def committee_members_menu(level: int, menu_name: MenuName, db: Database, committee_id: int,
                                 page: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'committee_members' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param committee_id: The ID of the committee.
    :param page: The current page number.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    committee = await db.get_committee(id=committee_id)
    members = await db.get_committee_members(committee.id)

    paginator = Paginator(members, page)
    members_on_page = paginator.get_page()
    pag_buttons = get_pag_buttons(paginator)

    text = render_template(menu_name=menu_name, committee_name=committee.name, committee_talisman=committee.talisman,
                           members=members)
    kb = get_committee_members_kb(
        level=level,
        menu_name=menu_name,
        members=members_on_page,
        page=page,
        pag_buttons=pag_buttons,
        committee_id=committee_id
    )

    return text, kb


async def person_menu(level: int, db: Database, menu_name: MenuName, person_id: int,
                      committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'person' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id, join_committees=True)

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           person_vk_id=person.vk_id)
    kb = get_person_kb(level=level, person=person, committee_id=committee_id)

    return text, kb


async def protocol_menu(level: int, db: Database, telegraph_api: TelegraphAPI, menu_name: MenuName, protocol_id: int,
                        committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'protocol' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param telegraph_api: The TelegraphAPI object.
    :param protocol_id: The ID of the protocol.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    protocol = await db.get_protocol(id=protocol_id, join_persons=True)
    committee = await db.get_committee(id=committee_id)
    all_points_added = await db.check_all_points_added(document_type=DocumentType.PROTOCOL, document_id=protocol_id)

    protocol_process_result_url = await get_document_process_result_url(
        document_type=DocumentType.PROTOCOL,
        document_id=protocol_id,
        db=db,
        telegraph_api=telegraph_api
    )

    text = render_template(menu_name=menu_name, protocol_number=protocol.number, protocol_date=protocol.date,
                           committee_name=committee.name, protocol_process_result_url=protocol_process_result_url)
    kb = get_protocol_kb(level=level, protocol_id=protocol_id, all_points_added=all_points_added,
                         committee_id=committee_id)

    return text, kb


def add_person_menu(level: int, menu_name: MenuName, current_state: str, fsm_data: dict) -> (str, InlineKeyboardMarkup):
    """
    Returns 'add_person' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param current_state: The current state of the finite state machine.
    :param fsm_data: The data for the finite state machine.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    vk_url = fsm_data.get('vk_url')
    first_name = fsm_data.get('first_name')
    last_name = fsm_data.get('last_name')
    committee_name = fsm_data.get('committee_name')
    error_valid = fsm_data.get('error_valid')
    all_valid = fsm_data.get('all_valid')

    text = render_template(menu_name=menu_name, current_state=current_state, vk_url=vk_url, first_name=first_name,
                           last_name=last_name, committee_name=committee_name, error_valid=error_valid,
                           all_valid=all_valid)
    kb = get_add_person_kb(level, all_valid)

    return text, kb


async def add_event_registration_table_menu(db: Database, level: int, menu_name: MenuName, current_state: str,
                                            fsm_data: dict, event_type_id: int) -> (str, InlineKeyboardMarkup):
    all_valid = fsm_data.get('all_valid')
    error_valid = fsm_data.get('error_valid')
    table_url = fsm_data.get('table_url')
    event_type = await db.get_event_type_name(event_type_id)

    text = render_template(menu_name=menu_name, current_state=current_state, all_valid=all_valid,
                           error_valid=error_valid, table_url=table_url, event_type=event_type)
    kb = get_add_event_registration_table_kb(level, all_valid, event_type_id)

    return text, kb


async def event_registration_tables_main_menu(level: int, menu_name: MenuName) -> (str, InlineKeyboardMarkup):
    text = render_template(menu_name=menu_name)
    kb = get_event_registration_tables_main_kb(level)

    return text, kb


async def event_registration_tables_menu(level: int, menu_name: MenuName, db: Database, google_api: GoogleAPI,
                                         page: int) -> (str, InlineKeyboardMarkup):
    tables = await db.get_event_registration_tables()

    await process_event_registration_tables(db=db, google_api=google_api)

    paginator = Paginator(tables, page)
    tables_on_page = paginator.get_page()
    pag_buttons = get_pag_buttons(paginator)

    text = render_template(menu_name=menu_name, tables=tables)
    kb = get_event_registration_tables_kb(
        level=level,
        menu_name=menu_name,
        tables=tables_on_page,
        page=page,
        pag_buttons=pag_buttons
    )

    return text, kb


async def event_registration_table_menu(level: int, menu_name: MenuName, db: Database, table_id: int,
                                        telegraph_api: TelegraphAPI) -> (str, InlineKeyboardMarkup):
    table = await db.get_event_registration_table(id=table_id)
    event_points = await db.get_event_type_points(event_type_id=table.event_type_id)
    all_points_added = await db.check_all_points_added(document_type=DocumentType.EVENT_REGISTRATION_TABLE,
                                                       document_id=table_id)

    table_process_result_url = await get_document_process_result_url(
        document_type=DocumentType.EVENT_REGISTRATION_TABLE,
        document_id=table_id,
        db=db,
        telegraph_api=telegraph_api
    )

    text = render_template(menu_name=menu_name, table_title=table.title, table_url=table.table_url,
                           table_process_result_url=table_process_result_url)
    kb = get_event_registration_table_kb(level=level, table_id=table_id, all_points_added=all_points_added,
                                         event_points=event_points)

    return text, kb


async def update_person_name_menu(level: int, menu_name: MenuName, db: Database, person_id: int, fsm_data: dict,
                                  committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'update_person_name' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :param fsm_data: The data for the finite state machine.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id)
    all_valid = fsm_data.get('all_valid')
    first_name = fsm_data.get('first_name')
    last_name = fsm_data.get('last_name')

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           fsm_data=fsm_data)
    kb = get_update_person_name_kb(level=level, all_valid=all_valid, first_name=first_name, last_name=last_name,
                                   person_id=person_id, committee_id=committee_id)

    return text, kb


async def person_points_menu(level: int, menu_name: MenuName, db: Database, person_id: int,
                             committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'person_points' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id, join_points=True)

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name)
    kb = get_person_points_kb(level, person, committee_id)

    return text, kb


async def person_committee_menu(
        level: int,
        menu_name: MenuName,
        db: Database,
        person_id: int,
        committee_id: int,
        current_person_committee_id: int
) -> (str, InlineKeyboardMarkup):
    """
    Returns 'person_committee' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :param current_person_committee_id: The ID of the person's current committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id, join_committees=True)
    current_person_committee = await db.get_committee(id=current_person_committee_id)
    person_committees_cnt = len(person.committees)

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           committee_name=current_person_committee.name, committees_cnt=person_committees_cnt)
    kb = get_person_committee_kb(level, person, committee_id, current_person_committee_id, person_committees_cnt)

    return text, kb


async def delete_person_menu(level: int, menu_name: MenuName, db: Database, person_id: int,
                             committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'delete_person' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id)

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name)
    kb = get_delete_person_kb(level, person_id=person_id, committee_id=committee_id)

    return text, kb


async def add_person_committee_menu(level: int, menu_name: MenuName, db: Database, person_id: int,
                                    committee_id: int) -> (str, InlineKeyboardMarkup):
    """
    Returns 'add_person_committee' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id, join_committees=True)
    committees = await db.get_committees()

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name)
    kb = get_add_person_committee_kb(level=level, committee_id=committee_id, person=person, committees=committees)

    return text, kb


async def points_in_category_menu(
        level: int,
        menu_name: MenuName,
        db: Database,
        person_id: int,
        committee_id: int,
        category_id: int,
        current_points: int,
        old_points: int
) -> (str, InlineKeyboardMarkup):
    """
    Returns 'points_in_category' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :param category_id: The ID of the category.
    :param current_points: The current points.
    :param old_points: The old points.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id)
    category = await db.get_category(id=category_id)

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           category_name=category.name)
    kb = get_points_in_category_kb(
        level=level,
        menu_name=menu_name,
        person_id=person_id,
        category_id=category_id,
        committee_id=committee_id,
        current_points=current_points,
        old_points=old_points
    )

    return text, kb


async def comment_for_update_points_menu(
        level: int,
        menu_name: MenuName,
        db: Database,
        committee_id: int,
        person_id: int,
        category_id: int,
        current_points: int,
        old_points: int,
        fsm_data: dict,
        current_state: str
) -> (str, InlineKeyboardMarkup):
    """
    Returns 'comment_for_update_points' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :param category_id: The ID of the category.
    :param current_points: The current points.
    :param old_points: The old points.
    :param fsm_data: The Finite State Machine data.
    :param current_state: The current state of the Finite State Machine.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id)
    category = await db.get_category(id=category_id)
    comment = fsm_data.get('comment')

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           category_name=category.name, comment=comment, current_state=current_state)
    kb = get_comment_for_update_points_kb(
        level=level,
        person_id=person_id,
        category_id=category_id,
        committee_id=committee_id,
        current_points=current_points,
        old_points=old_points,
        comment=comment,
        current_state=current_state
    )

    return text, kb


async def select_event_type_menu(level: int, menu_name: MenuName, db: Database) -> (str, InlineKeyboardMarkup):
    event_types = await db.get_event_types()

    text = render_template(menu_name=menu_name)
    kb = get_select_event_type_kb(level=level, event_types=event_types)

    return text, kb


async def update_person_committee_menu(
        level: int,
        menu_name: MenuName,
        db: Database,
        committee_id: int,
        person_id: int,
        current_person_committee_id: int
) -> (str, InlineKeyboardMarkup):
    """
    Returns 'update_person_committee' menu content.
    :param level: The level of the menu.
    :param menu_name: The name of the menu.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :param current_person_committee_id: The ID of the person's current committee.
    :return: A tuple containing the text for the menu and the keyboard markup.
    """
    person = await db.get_person(id=person_id, join_committees=True)
    current_person_committee = await db.get_committee(id=current_person_committee_id)
    committees = await db.get_committees()

    text = render_template(menu_name=menu_name, person_first_name=person.first_name, person_last_name=person.last_name,
                           committee_name=current_person_committee.name)
    kb = get_update_person_committee_kb(
        level=level,
        person=person,
        committee_id=committee_id,
        current_person_committee=current_person_committee,
        committees=committees
    )

    return text, kb


async def get_menu_content(
        callback_data: MenuCallback,
        fsm_data: dict | None = None,
        db: Database | None = None,
        google_api: GoogleAPI | None = None,
        telegraph_api: TelegraphAPI | None = None,
        current_state: str | None = None
) -> (str, InlineKeyboardMarkup):
    """
    Retrieves the menu content based on the provided callback data.
    It handles different levels and menu names, and interacts with the database and Google API.
    :param callback_data: The callback data containing menu information.
    :param fsm_data: The Finite State Machine data.
    :param db: The Database object.
    :param google_api: The GoogleAPI object.
    :param telegraph_api: The TelegraphAPI object.
    :param current_state: The current state of the Finite State Machine.
    :return: The menu content as a string and an inline keyboard markup.
    """
    level = callback_data.level
    menu_name = callback_data.menu_name
    committee_id = callback_data.committee_id
    person_id = callback_data.person_id
    protocol_id = callback_data.protocol_id
    category_id = callback_data.category_id
    table_id = callback_data.table_id
    event_type_id = callback_data.event_type_id
    current_points = callback_data.current_points
    old_points = callback_data.old_points
    current_person_committee_id = callback_data.current_person_committee_id
    page = callback_data.page

    if level == 0:
        return start_menu(level=level, menu_name=menu_name)

    elif level == 1:
        if menu_name == MenuName.ADD_PERSON:
            return add_person_menu(
                level=level,
                menu_name=menu_name,
                current_state=current_state,
                fsm_data=fsm_data
            )
        elif menu_name == MenuName.SELECT_COMMITTEE:
            return await select_committee_menu(level=level, menu_name=menu_name, db=db)
        elif menu_name == MenuName.EVENT_REGISTRATION_TABLES_MAIN:
            return await event_registration_tables_main_menu(level=level, menu_name=menu_name)

    elif level == 2:
        if menu_name == MenuName.COMMITTEE:
            return await committee_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                committee_id=committee_id,
            )
        elif menu_name == MenuName.EVENT_REGISTRATION_TABLES:
            return await event_registration_tables_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                google_api=google_api,
                page=page
            )
        elif menu_name == MenuName.SELECT_EVENT_TYPE:
            return await select_event_type_menu(
                db=db,
                level=level,
                menu_name=menu_name
            )

    elif level == 3:
        if menu_name == MenuName.COMMITTEE_MEMBERS:
            return await committee_members_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                committee_id=committee_id,
                page=page
            )
        elif menu_name == MenuName.COMMITTEE_PROTOCOLS:
            return await committee_protocols_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                google_api=google_api,
                committee_id=committee_id,
                page=page
            )
        elif menu_name == MenuName.EVENT_REGISTRATION_TABLE:
            return await event_registration_table_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                table_id=table_id,
                telegraph_api=telegraph_api
            )
        elif menu_name == MenuName.ADD_EVENT_REGISTRATION_TABLE:
            return await add_event_registration_table_menu(
                db=db,
                level=level,
                menu_name=menu_name,
                event_type_id=event_type_id,
                current_state=current_state,
                fsm_data=fsm_data
            )

    elif level == 4:
        if menu_name == MenuName.PERSON:
            return await person_menu(
                level=level,
                db=db,
                menu_name=menu_name,
                person_id=person_id,
                committee_id=committee_id
            )
        elif menu_name == MenuName.PROTOCOL:
            return await protocol_menu(
                level=level,
                db=db,
                menu_name=menu_name,
                protocol_id=protocol_id,
                committee_id=committee_id,
                telegraph_api=telegraph_api
            )

    elif level == 5:
        if menu_name == MenuName.PERSON_POINTS:
            return await person_points_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id
            )
        elif menu_name == MenuName.PERSON_COMMITTEE:
            return await person_committee_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id,
                current_person_committee_id=current_person_committee_id
            )
        elif menu_name == MenuName.DELETE_PERSON:
            return await delete_person_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id
            )
        elif menu_name == MenuName.ADD_PERSON_COMMITTEE:
            return await add_person_committee_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id
            )
        elif menu_name in (MenuName.UPDATE_FIRST_NAME, MenuName.UPDATE_LAST_NAME):
            return await update_person_name_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id,
                fsm_data=fsm_data
            )

    elif level == 6:
        if menu_name == MenuName.POINTS_IN_CATEGORY:
            return await points_in_category_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                category_id=category_id,
                current_points=current_points,
                old_points=old_points,
                committee_id=committee_id
            )
        elif menu_name == MenuName.UPDATE_PERSON_COMMITTEE:
            return await update_person_committee_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                committee_id=committee_id,
                current_person_committee_id=current_person_committee_id
            )

    elif level == 7:
        if menu_name == MenuName.COMMENT_FOR_UPDATE_POINTS:
            return await comment_for_update_points_menu(
                level=level,
                menu_name=menu_name,
                db=db,
                person_id=person_id,
                category_id=category_id,
                committee_id=committee_id,
                current_points=current_points,
                old_points=old_points,
                fsm_data=fsm_data,
                current_state=current_state
            )
