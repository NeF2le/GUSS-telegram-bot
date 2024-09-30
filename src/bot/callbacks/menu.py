from contextlib import suppress

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.bot.utils.callback_fabrics import MenuCallback
from src.bot.handlers.menu_content import get_menu_content
from src.config_reader import settings
from src.database import Database
from src.enums import ActionType, MenuName
from src.bot.utils.states import AddPerson, UpdatePerson, UpdatePersonPoints, AddEventRegistrationTable
from src.bot.utils.log_action import log_action, ContextData
from src.api import GoogleAPI, TelegraphAPI

router = Router()


async def add_person(callback: CallbackQuery, db: Database, first_name: str, last_name: str, vk_id: int,
                     committee_name: str):
    person_id = await db.insert_person(first_name, last_name, vk_id)
    committee_id = await db.get_committee_id(committee_name)

    context_data = ContextData()

    async with log_action(db=db, action_type=ActionType.INSERT_PERSON, username=callback.from_user.username,
                          context_data=context_data):
        try:
            await db.insert_membership(person_id, committee_id)
            await db.insert_person_points(person_id)

            context_data.person_id = person_id

            await callback.answer(f"{first_name} {last_name} добавлен(а) в ГУСС-топ!", show_alert=True)
        except Exception as e:
            await callback.answer("Произошла ошибка при добавлении человека в ГУСС-топ", show_alert=True)
            raise e


async def add_event_registration_table(callback: CallbackQuery, db: Database, table_url: str, table_title: str,
                                       event_type_id: int):
    try:
        await db.insert_event_registration_table(table_title, table_url, event_type_id)
        await callback.answer(f"Таблица регистраций '{table_title}' добавлена в ГУСС-топ!", show_alert=True)
    except Exception as e:
        await callback.answer("Произошла ошибка при добавлении таблицы регистраций в ГУСС-топ", show_alert=True)
        raise e


async def delete_person(callback: CallbackQuery, db: Database, person_id: int):
    """
    Deletes a person from the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person to be deleted.
    :return: None.
    """
    person = await db.get_person(id=person_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.DELETE_PERSON, username=callback.from_user.username,
                          context_data=context_data):
        try:
            await db.delete_person(person_id)
            context_data.person_id = None
            await callback.answer(f"{person.first_name} {person.last_name} удален(а) из ГУСС-топа!", show_alert=True)
        except Exception as e:
            await callback.answer("Произошла ошибка при удалении человека из БД", show_alert=True)
            raise e


async def add_person_committee(callback: CallbackQuery, db: Database, person_id: int, committee_id: int):
    """
    Adds a committee to a person in the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: None.
    """
    person = await db.get_person(id=person_id)
    committee = await db.get_committee(id=committee_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.INSERT_MEMBERSHIP, username=callback.from_user.username,
                          context_data=context_data):
        try:
            await db.insert_membership(person_id, committee_id)

            await callback.answer(
                f"{person.first_name} {person.last_name} теперь состоит также в {committee.name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при добавлении комитета человеку", show_alert=True)
            raise e


async def update_person_committee(callback: CallbackQuery, db: Database, person_id: int, current_committee_id: id,
                                  new_committee_id: id):
    """
    Updates a person's committee in the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param current_committee_id: The ID of the current committee.
    :param new_committee_id: The ID of the new committee.
    :return: None.
    """
    person = await db.get_person(id=person_id)
    current_committee = await db.get_committee(id=current_committee_id)
    new_committee = await db.get_committee(id=new_committee_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.UPDATE_MEMBERSHIP, username=callback.from_user.username,
                          context_data=context_data):
        try:
            await db.update_person_committee(person_id, current_committee.id, new_committee_id)

            await callback.answer(
                f"{person.first_name} {person.last_name} теперь состоит в {new_committee.name} вместо {current_committee.name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при изменении комитета у человека", show_alert=True)
            raise e


async def delete_person_committee(callback: CallbackQuery, db: Database, person_id: int, committee_id: int):
    """
    Deletes a person's committee from the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param committee_id: The ID of the committee.
    :return: None.
    """
    person = await db.get_person(id=person_id)
    committee = await db.get_committee(id=committee_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.DELETE_MEMBERSHIP, username=callback.from_user.username,
                          context_data=context_data):
        try:
            await db.delete_person_committee(person_id, committee_id)

            await callback.answer(
                f"{person.first_name} {person.last_name} больше не состоит в {committee.name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при удалении комитета у человека", show_alert=True)
            raise e


async def add_points_to_protocol_persons(db: Database, callback: CallbackQuery, committee_id: int, protocol_id: int):
    """
    Processes persons in a protocol and adds attendance points to the them based on their participation in the committee protocol.
    :param db: The Database object for database operations.
    :param callback: The CallbackQuery object for sending messages to the user.
    :param committee_id: The ID of the committee.
    :param protocol_id: The ID of the protocol.
    :return: None.
    """
    protocol_persons = await db.get_protocol_persons(protocol_id=protocol_id, points_added=False)
    for protocol_person in protocol_persons:
        matched_person_id = protocol_person.matched_person_id
        if not matched_person_id:
            continue

        await add_committee_attendance_points(callback=callback, db=db, person_id=matched_person_id,
                                              protocol_id=protocol_id, committee_id=committee_id)
        await db.update_points_added_mark_in_protocol_person(protocol_person.id)

    with suppress(TelegramBadRequest):
        await callback.answer('Баллы за посещение комитета успешно добавлены', show_alert=True)


async def add_points_to_table_persons(db: Database, callback: CallbackQuery, table_id: int, points: int):
    table_title = await db.get_event_registration_table_title(id=table_id)

    table_persons = await db.get_event_registration_table_persons(table_id=table_id, points_added=False)

    for table_person in table_persons:
        matched_person_id = table_person.matched_person_id
        if not matched_person_id:
            continue

        await add_event_attendance_points(callback=callback, db=db, person_id=matched_person_id, event=table_title,
                                          points=points)
        await db.update_points_added_mark_in_table_person(table_person.id)

    with suppress(TelegramBadRequest):
        await callback.answer('Баллы за посещение мероприятия успешно добавлены', show_alert=True)


async def add_committee_attendance_points(callback: CallbackQuery, db: Database, protocol_id: int,
                                          person_id: int, committee_id: int):
    attendance_category = await db.get_category(name='Посещаемость')
    committee_name = await db.get_committee_name(committee_id)
    protocol_date = await db.get_protocol_date(protocol_id)

    comment = f"Посещение {committee_name} за {protocol_date}"
    context_data = ContextData(person_id=person_id, comment=comment)

    async with log_action(db=db, action_type=ActionType.UPDATE_PERSON_POINTS, username=callback.from_user.username,
                          context_data=context_data):
        await db.update_person_points(person_id, attendance_category.id, settings.COMMITTEE_ATTENDANCE_POINTS)


async def add_event_attendance_points(callback: CallbackQuery, db: Database, person_id: int, event: str, points: int):
    attendance_category = await db.get_category(name='Посещаемость')

    comment = f"Посещение {event}"
    context_data = ContextData(person_id=person_id, comment=comment)

    async with log_action(db=db, action_type=ActionType.UPDATE_PERSON_POINTS, username=callback.from_user.username,
                          context_data=context_data):
        await db.update_person_points(person_id, attendance_category.id, points)


async def update_person_points(callback: CallbackQuery, db: Database, person_id: int, category_id: int, new_value: int,
                               comment: str):
    """
    Updates a person's points in a specific category in the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param category_id: The ID of the category.
    :param new_value: The new value of points.
    :param comment: The comment for the update.
    :return: None.
    """
    person = await db.get_person(id=person_id)
    category = await db.get_category(id=category_id)

    context_data = ContextData(person_id=person_id, comment=comment)

    async with log_action(db=db, action_type=ActionType.UPDATE_PERSON_POINTS, username=callback.from_user.username,
                          context_data=context_data):
        try:
            original_points = (await db.get_person_points(person_id=person_id, category_id=category_id)).points_value
            await db.update_person_points(person_id, category_id, new_value - original_points)

            await callback.answer(
                f"{person.first_name} {person.last_name} теперь имеет {new_value} баллов в категории {category.name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при изменении баллов у человека", show_alert=True)
            raise e


async def update_first_name(callback: CallbackQuery, db: Database, person_id: int, new_first_name: str):
    """
    Updates a person's first name in the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param new_first_name: The new first name.
    :return: None.
    """
    person = await db.get_person(id=person_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.UPDATE_PERSON_FIRST_NAME,
                          username=callback.from_user.username, context_data=context_data):
        try:
            await db.update_person_name(person_id=person_id, new_first_name=new_first_name)

            await callback.answer(
                f"{person.first_name} {person.last_name} теперь {new_first_name} {person.last_name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при изменении имени у человека", show_alert=True)
            raise e


async def update_last_name(callback: CallbackQuery, db: Database, person_id: int, new_last_name: str):
    """
    Updates a person's last name in the database.
    :param callback: The CallbackQuery object.
    :param db: The Database object.
    :param person_id: The ID of the person.
    :param new_last_name: The new last name.
    :return: None.
    """
    person = await db.get_person(id=person_id)

    context_data = ContextData(person_id=person_id)

    async with log_action(db=db, action_type=ActionType.UPDATE_PERSON_LAST_NAME,
                          username=callback.from_user.username, context_data=context_data):
        try:
            await db.update_person_name(person_id=person_id, new_last_name=new_last_name)

            await callback.answer(
                f"{person.first_name} {person.last_name} теперь {person.first_name} {new_last_name}",
                show_alert=True
            )
        except Exception as e:
            await callback.answer("Произошла ошибка при изменении фамилии у человека", show_alert=True)
            raise e


async def update_state(cur_state: FSMContext, new_state: str, callback: CallbackQuery,
                       callback_data: MenuCallback) -> str:
    """
    Updates the state in the finite state machine (FSM) context.
    :param cur_state: The current state in the FSM context.
    :param new_state: The new state to be set in the FSM context.
    :param callback: The CallbackQuery object.
    :param callback_data: The MenuCallback object.
    :return: The new state set in the FSM context.
    """
    await cur_state.set_state(new_state)
    await cur_state.update_data(callback=callback)
    await cur_state.update_data(callback_data=callback_data)
    return await cur_state.get_state()


async def handle_confirm_add_person(callback: CallbackQuery, db: Database, state: FSMContext,
                                    fsm_data: dict) -> (int, MenuName):
    first_name = fsm_data.get('first_name')
    last_name = fsm_data.get('last_name')
    vk_id = fsm_data.get('vk_id')
    committee_name = fsm_data.get('committee_name')

    await add_person(callback, db, first_name, last_name, vk_id, committee_name)
    await state.clear()
    return 0, MenuName.START


async def handle_confirm_update_first_name(callback: CallbackQuery, db: Database, state: FSMContext,
                                           callback_data: MenuCallback, fsm_data: dict) -> (int, MenuName):
    person_id = callback_data.person_id
    first_name = fsm_data.get('first_name')

    await update_first_name(callback, db, person_id, first_name)
    await state.clear()
    return 4, MenuName.PERSON


async def handle_confirm_update_last_name(callback: CallbackQuery, db: Database, state: FSMContext,
                                          callback_data: MenuCallback, fsm_data: dict) -> (int, MenuName):
    person_id = callback_data.person_id
    last_name = fsm_data.get('last_name')

    await update_last_name(callback, db, person_id, last_name)
    await state.clear()
    return 4, MenuName.PERSON


async def handle_confirm_delete_person(callback: CallbackQuery, db: Database,
                                       callback_data: MenuCallback) -> (int, MenuName):
    person_id = callback_data.person_id

    await delete_person(callback=callback, db=db, person_id=person_id)
    return 2, MenuName.COMMITTEE


async def handle_confirm_add_committee_attendance_points(callback: CallbackQuery, db: Database,
                                                         callback_data: MenuCallback) -> (int, MenuName):
    committee_id = callback_data.committee_id
    protocol_id = callback_data.protocol_id

    await add_points_to_protocol_persons(db=db, callback=callback, committee_id=committee_id, protocol_id=protocol_id)
    return 4, MenuName.PROTOCOL


async def handle_confirm_add_person_committee(callback: CallbackQuery, db: Database,
                                              callback_data: MenuCallback) -> (int, MenuName):
    person_id = callback_data.person_id
    new_person_committee_id = callback_data.new_person_committee_id

    await add_person_committee(callback=callback, db=db, person_id=person_id, committee_id=new_person_committee_id)
    return 4, MenuName.PERSON


async def handle_confirm_update_person_committee(callback: CallbackQuery, db: Database,
                                                 callback_data: MenuCallback) -> (int, MenuName):
    person_id = callback_data.person_id
    current_person_committee_id = callback_data.current_person_committee_id
    new_person_committee_id = callback_data.new_person_committee_id

    await update_person_committee(callback=callback, db=db, person_id=person_id,
                                  current_committee_id=current_person_committee_id,
                                  new_committee_id=new_person_committee_id)
    return 4, MenuName.PERSON


async def handle_confirm_delete_person_committee(callback: CallbackQuery, db: Database,
                                                 callback_data: MenuCallback) -> (int, MenuName):
    person_id = callback_data.person_id
    current_person_committee_id = callback_data.current_person_committee_id

    await delete_person_committee(callback=callback, db=db, person_id=person_id,
                                  committee_id=current_person_committee_id)
    return 4, MenuName.PERSON


async def handle_confirm_update_points(callback: CallbackQuery, db: Database, fsm_data: dict,
                                       callback_data: MenuCallback) -> (int, MenuName):
    person_id = callback_data.person_id
    category_id = callback_data.category_id
    current_points = callback_data.current_points

    await update_person_points(callback=callback, db=db, person_id=person_id, category_id=category_id,
                               new_value=current_points, comment=fsm_data.get('comment'))
    return 4, MenuName.PERSON


async def handle_confirm_add_event_registration_table(callback: CallbackQuery, db: Database, callback_data: MenuCallback,
                                                      fsm_data: dict) -> (int, MenuName):
    table_url = fsm_data.get('table_url')
    table_title = fsm_data.get('table_title')
    event_type_id = callback_data.event_type_id

    await add_event_registration_table(callback=callback, db=db, table_url=table_url, table_title=table_title,
                                       event_type_id=event_type_id)
    return 1, MenuName.EVENT_REGISTRATION_TABLES_MAIN


async def handle_confirm_add_event_attendance_points(callback: CallbackQuery, db: Database,
                                                     callback_data: MenuCallback) -> (int, MenuName):
    table_id = callback_data.table_id
    edit_points = callback_data.edit_points

    await add_points_to_table_persons(db=db, callback=callback, table_id=table_id, points=edit_points)
    return 3, MenuName.EVENT_REGISTRATION_TABLE


async def handle_state_transitions(menu_name: MenuName, state: FSMContext, callback: CallbackQuery,
                                   callback_data: MenuCallback) -> str:
    new_state = ""
    if menu_name == MenuName.ADD_PERSON:
        new_state = AddPerson.vk_url
    elif menu_name == MenuName.ADD_EVENT_REGISTRATION_TABLE:
        new_state = AddEventRegistrationTable.table_url
    elif menu_name == MenuName.UPDATE_FIRST_NAME:
        new_state = UpdatePerson.first_name
    elif menu_name == MenuName.UPDATE_LAST_NAME:
        new_state = UpdatePerson.last_name
    elif menu_name == MenuName.COMMENT_FOR_UPDATE_POINTS:
        new_state = UpdatePersonPoints.comment

    return await update_state(state, new_state, callback, callback_data)


async def handle_fsm_state(state: FSMContext, is_back_button: bool) -> (str, dict):
    """
    Handles the FSM state based on back button press.
    """
    current_state = await state.get_state()
    fsm_data = await state.get_data()

    if current_state and is_back_button:
        await state.clear()
        return "", {}

    return current_state, fsm_data


async def adapt_handler(handler, callback: CallbackQuery, db: Database, callback_data: MenuCallback,
                        state: FSMContext, fsm_data: dict):
    """
    Adapts the handler to accept only the arguments it needs.
    """
    handler_params = handler.__code__.co_varnames

    args = {
        'callback': callback,
        'db': db
    }

    if 'callback_data' in handler_params:
        args['callback_data'] = callback_data

    if 'state' in handler_params:
        args['state'] = state

    if 'fsm_data' in handler_params:
        args['fsm_data'] = fsm_data

    return await handler(**args)


CONFIRM_HANDLERS = {
    MenuName.CONFIRM_ADD_PERSON: handle_confirm_add_person,
    MenuName.CONFIRM_UPDATE_FIRST_NAME: handle_confirm_update_first_name,
    MenuName.CONFIRM_UPDATE_LAST_NAME: handle_confirm_update_last_name,
    MenuName.ADD_COMMITTEE_ATTENDANCE_POINTS: handle_confirm_add_committee_attendance_points,
    MenuName.CONFIRM_DELETE_PERSON: handle_confirm_delete_person,
    MenuName.CONFIRM_ADD_PERSON_COMMITTEE: handle_confirm_add_person_committee,
    MenuName.CONFIRM_UPDATE_PERSON_COMMITTEE: handle_confirm_update_person_committee,
    MenuName.CONFIRM_DELETE_PERSON_COMMITTEE: handle_confirm_delete_person_committee,
    MenuName.CONFIRM_UPDATE_PERSON_POINTS: handle_confirm_update_points,
    MenuName.CONFIRM_ADD_EVENT_REGISTRATION_TABLE: handle_confirm_add_event_registration_table,
    MenuName.CONFIRM_ADD_EVENT_ATTENDANCE_POINTS: handle_confirm_add_event_attendance_points
}


@router.callback_query(MenuCallback.filter())
async def user_menu(callback: CallbackQuery, callback_data: MenuCallback, db: Database, state: FSMContext,
                    google_api: GoogleAPI | None = None, telegraph_api: TelegraphAPI | None = None):
    """
    Handles callback queries for user menu interactions.
    :param telegraph_api:
    :param callback: The CallbackQuery object.
    :param callback_data: The MenuCallback object.
    :param db: The Database object.
    :param state: The FSMContext object.
    :param google_api: The GoogleAPI object (optional).
    :return: None.
    """
    current_points = callback_data.current_points
    edit_points = callback_data.edit_points
    menu_name = callback_data.menu_name

    current_state, fsm_data = await handle_fsm_state(state, callback_data.is_back_button)

    if not current_state:
        current_state = await handle_state_transitions(menu_name=menu_name, state=state, callback=callback,
                                                       callback_data=callback_data)

    if menu_name == MenuName.POINTS_IN_CATEGORY and edit_points:
        current_points += edit_points
        callback_data.current_points = 0 if current_points < 0 else current_points

    handler = CONFIRM_HANDLERS.get(menu_name)
    if handler:
        callback_data.level, callback_data.menu_name = await adapt_handler(
            handler=handler,
            callback=callback,
            db=db,
            callback_data=callback_data,
            state=state,
            fsm_data=fsm_data
        )

    text, kb = await get_menu_content(
        callback_data=callback_data,
        fsm_data=fsm_data,
        db=db,
        google_api=google_api,
        current_state=current_state,
        telegraph_api=telegraph_api
    )

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=text,
            reply_markup=kb,
            disable_web_page_preview=True
        )

        await callback.answer()
