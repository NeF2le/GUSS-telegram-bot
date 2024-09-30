from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.utils.callback_fabrics import MenuCallback
from src.database.models import Person, Committee, Protocol, EventRegistrationTable, EventType
from src.enums import MenuName


def _create_inline_button(text: str, callback_data: MenuCallback | str) -> InlineKeyboardButton:
    """
    Creates an inline keyboard button with the given text and callback data.
    :param text: The text to be displayed on the button.
    :param callback_data: The callback data to be sent when the button is clicked.
        If the callback data is a MenuCallback, it will be packed into a string.
    :return:
    """
    if isinstance(callback_data, MenuCallback):
        callback_data = callback_data.pack()
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def _create_back_button(level: int, menu_name: MenuName, **kwargs) -> InlineKeyboardButton:
    """
    Creates a back inline button with the given level and menu name.
    :param level: The level of the menu to go back to.
    :param menu_name: The name of the menu to go back to.
    :param kwargs: Additional parameters to be included in the callback data.
    :return: An inline keyboard button with the back text and callback data.
    """
    return InlineKeyboardButton(
        text="Назад",
        callback_data=MenuCallback(level=level - 1, menu_name=menu_name, is_back_button=True, **kwargs).pack()
    )


def get_start_kb(level: int = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button("Выбрать комитет", MenuCallback(level=level + 1, menu_name=MenuName.SELECT_COMMITTEE)))
    kb.row(_create_inline_button("Добавить человека", MenuCallback(level=level + 1, menu_name=MenuName.ADD_PERSON)))
    kb.row(_create_inline_button("Таблицы регистраций",
                                 MenuCallback(level=level + 1, menu_name=MenuName.EVENT_REGISTRATION_TABLES_MAIN)))
    kb.row(_create_inline_button("Выгрузить статистику ГУСС-топа", "guss_top_stats"))
    kb.row(_create_inline_button("Выгрузить историю действий", "action_logs"))

    return kb.as_markup()


def get_event_registration_tables_main_kb(level: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button("Выбрать таблицу",
                                 MenuCallback(level=level + 1, menu_name=MenuName.EVENT_REGISTRATION_TABLES)))
    kb.row(_create_inline_button("Добавить таблицу",
                                 MenuCallback(level=level + 1, menu_name=MenuName.SELECT_EVENT_TYPE)))
    kb.row(_create_back_button(level, menu_name=MenuName.START))

    return kb.as_markup()


def get_add_event_registration_table_kb(level: int, all_valid: bool, event_type_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if all_valid:
        kb.row(
            _create_inline_button(
                "✅ Подтвердить ✅",
                MenuCallback(level=level, menu_name=MenuName.CONFIRM_ADD_EVENT_REGISTRATION_TABLE,
                             event_type_id=event_type_id))
        )

    kb.row(_create_back_button(level, MenuName.SELECT_EVENT_TYPE))

    return kb.as_markup()


def get_select_event_type_kb(level: int, event_types: list[EventType]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for event_type in event_types:
        kb.add(_create_inline_button(
            f"{event_type.name}",
            MenuCallback(level=level + 1, menu_name=MenuName.ADD_EVENT_REGISTRATION_TABLE, event_type_id=event_type.id)
        ))
    kb.adjust(2)

    kb.row(_create_back_button(level, MenuName.EVENT_REGISTRATION_TABLES_MAIN))

    return kb.as_markup()


def get_event_registration_tables_kb(
        level: int,
        menu_name: MenuName,
        tables: list[EventRegistrationTable],
        page: int,
        pag_buttons: dict[str, str],
        sizes: int | list[int] = 1
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for table in tables:
        kb.add(_create_inline_button(
            f"{table.title}",
            MenuCallback(level=level + 1, menu_name=MenuName.EVENT_REGISTRATION_TABLE, table_id=table.id)
        ))

    sizes = [sizes] if isinstance(sizes, int) else sizes
    kb.adjust(*sizes)

    row = []
    for text, action in pag_buttons.items():
        if action == "next":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page + 1)
            ))

        if action == "prev":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page - 1)
            ))
    kb.row(*row)

    kb.row(_create_back_button(level, MenuName.EVENT_REGISTRATION_TABLES_MAIN))

    return kb.as_markup()


def get_event_registration_table_kb(level: int, table_id: int, all_points_added: bool,
                                    event_points: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if not all_points_added:
        kb.row(_create_inline_button(
            "Выставить баллы",
            MenuCallback(level=level, menu_name=MenuName.ADD_EVENT_ATTENDANCE_POINTS, table_id=table_id,
                         edit_points=event_points))
        )
    kb.row(_create_back_button(level, MenuName.EVENT_REGISTRATION_TABLES))

    return kb.as_markup()


def get_add_person_kb(level: int, all_valid: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if all_valid:
        kb.row(
            _create_inline_button("✅ Подтвердить ✅", MenuCallback(level=level, menu_name=MenuName.CONFIRM_ADD_PERSON)))

    kb.row(_create_back_button(level, MenuName.START))

    return kb.as_markup()


def get_select_committee_kb(level: int, committees: list[Committee],
                            sizes: int | list[int] = 2) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for com in committees:
        kb.add(_create_inline_button(
            f"{com.talisman} {com.name} {com.talisman}",
            MenuCallback(level=level + 1, menu_name=MenuName.COMMITTEE, committee_id=com.id)
        ))
    sizes = [sizes] if isinstance(sizes, int) else sizes
    kb.adjust(*sizes)

    kb.row(_create_back_button(level, MenuName.START))

    return kb.as_markup()


def get_committee_kb(level: int, committee_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button(
        "Участники",
        MenuCallback(level=level + 1, menu_name=MenuName.COMMITTEE_MEMBERS, committee_id=committee_id)
    ))
    kb.row(_create_inline_button(
        "Протоколы",
        MenuCallback(level=level + 1, menu_name=MenuName.COMMITTEE_PROTOCOLS, committee_id=committee_id)
    ))
    kb.row(_create_back_button(level, menu_name=MenuName.SELECT_COMMITTEE, committee_id=committee_id))

    return kb.as_markup()


def get_committee_protocols_kb(
        level: int,
        menu_name: MenuName,
        committee_id: int,
        protocols: list[Protocol],
        page: int,
        pag_buttons: dict[str, str],
        sizes: int | list[int] = 1
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for protocol in protocols:
        kb.add(_create_inline_button(
            f"Протокол №{protocol.number} {protocol.date}",
            MenuCallback(level=level + 1, menu_name=MenuName.PROTOCOL, committee_id=committee_id,
                         protocol_id=protocol.id)
        ))

    sizes = [sizes] if isinstance(sizes, int) else sizes
    kb.adjust(*sizes)

    row = []
    for text, action in pag_buttons.items():
        if action == "next":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page + 1, committee_id=committee_id)
            ))

        if action == "prev":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page - 1, committee_id=committee_id)
            ))
    kb.row(*row)

    kb.row(_create_back_button(level, MenuName.COMMITTEE, committee_id=committee_id))

    return kb.as_markup()


def get_committee_members_kb(
        level: int,
        menu_name: MenuName,
        members: list[Person],
        committee_id: int,
        page: int,
        pag_buttons: dict[str, str],
        sizes: int | list[int] = 1
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for member in members:
        kb.add(_create_inline_button(
            f"{member.first_name} {member.last_name}",
            MenuCallback(level=level + 1, menu_name=MenuName.PERSON, person_id=member.id, committee_id=committee_id)
        ))

    sizes = [sizes] if isinstance(sizes, int) else sizes
    kb.adjust(*sizes)

    row = []
    for text, action in pag_buttons.items():
        if action == "next":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page + 1, committee_id=committee_id)
            ))

        if action == "prev":
            row.append(_create_inline_button(
                text,
                MenuCallback(level=level, menu_name=menu_name, page=page - 1, committee_id=committee_id)
            ))
    kb.row(*row)

    kb.row(_create_back_button(level, MenuName.COMMITTEE, committee_id=committee_id))

    return kb.as_markup()


def get_person_kb(level: int, person: Person, committee_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button(
        "Баллы",
        MenuCallback(level=level + 1, menu_name=MenuName.PERSON_POINTS, person_id=person.id, committee_id=committee_id)
    ))

    person_committees_cnt = len(person.committees)
    if person_committees_cnt == 1:
        committee = person.committees[0]
        kb.row(_create_inline_button(
            f"{committee.talisman} {committee.name} {committee.talisman}",
            MenuCallback(level=level + 1, menu_name=MenuName.PERSON_COMMITTEE, person_id=person.id,
                         committee_id=committee_id,
                         current_person_committee_id=committee.id)
        ))

        kb.row(_create_inline_button(
            "Добавить комитет",
            MenuCallback(level=level + 1, menu_name=MenuName.ADD_PERSON_COMMITTEE, person_id=person.id,
                         committee_id=committee_id,
                         current_person_committee_id=committee.id)
        ))

    if person_committees_cnt > 1:
        row = []
        for com in person.committees:
            row.append(_create_inline_button(
                f"{com.talisman} {com.name} {com.talisman}",
                MenuCallback(level=level + 1, menu_name=MenuName.PERSON_COMMITTEE, person_id=person.id,
                             committee_id=committee_id,
                             current_person_committee_id=com.id)
            ))
        kb.row(*row)

    kb.row(_create_inline_button(
        "Изменить имя",
        MenuCallback(level=level + 1, menu_name=MenuName.UPDATE_FIRST_NAME, person_id=person.id,
                     committee_id=committee_id)
    ), _create_inline_button(
        "Изменить фамилию",
        MenuCallback(level=level + 1, menu_name=MenuName.UPDATE_LAST_NAME, person_id=person.id,
                     committee_id=committee_id)
    ))

    kb.row(_create_inline_button(
        "❌ Удалить ❌",
        MenuCallback(level=level + 1, menu_name=MenuName.DELETE_PERSON, person_id=person.id, committee_id=committee_id)
    ))

    kb.row(_create_back_button(level, MenuName.COMMITTEE_MEMBERS, committee_id=committee_id))

    return kb.as_markup()


def get_protocol_kb(level: int, all_points_added: bool, protocol_id: int, committee_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if not all_points_added:
        kb.row(_create_inline_button(
            "Выставить баллы",
            MenuCallback(level=level, menu_name=MenuName.ADD_COMMITTEE_ATTENDANCE_POINTS, committee_id=committee_id,
                         protocol_id=protocol_id)
        ))

    kb.row(_create_back_button(level=level, menu_name=MenuName.COMMITTEE_PROTOCOLS, committee_id=committee_id))

    return kb.as_markup()


def get_update_person_name_kb(level: int, person_id: int, committee_id: int, all_valid: bool,
                              first_name: str | None, last_name: str | None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if all_valid and first_name:
        kb.row(_create_inline_button(
            "✅ Подтвердить ✅",
            MenuCallback(level=level, menu_name=MenuName.CONFIRM_UPDATE_FIRST_NAME, person_id=person_id,
                         committee_id=committee_id)
        ))

    if all_valid and last_name:
        kb.row(_create_inline_button(
            "✅ Подтвердить ✅",
            MenuCallback(level=level, menu_name=MenuName.CONFIRM_UPDATE_LAST_NAME, person_id=person_id,
                         committee_id=committee_id)
        ))

    kb.row(_create_back_button(level, MenuName.PERSON, person_id=person_id, committee_id=committee_id))

    return kb.as_markup()


def get_person_points_kb(level: int, person: Person, committee_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    categories_row = []
    for p in person.points:
        points_value = p.points_value
        categories_row.append(_create_inline_button(
            p.category.name,
            MenuCallback(level=level + 1, menu_name=MenuName.POINTS_IN_CATEGORY, person_id=person.id,
                         category_id=p.category.id,
                         current_points=points_value, old_points=points_value, committee_id=committee_id)
        ))
    kb.row(*categories_row)

    points_values_row = []
    for p in person.points:
        points_value = p.points_value
        points_values_row.append(_create_inline_button(
            str(points_value),
            MenuCallback(level=level + 1, menu_name=MenuName.POINTS_IN_CATEGORY, person_id=person.id,
                         category_id=p.category.id,
                         current_points=points_value, old_points=points_value, committee_id=committee_id)
        ))
    kb.row(*points_values_row)

    kb.row(_create_back_button(level, MenuName.PERSON, person_id=person.id, committee_id=committee_id))

    return kb.as_markup()


def get_person_committee_kb(level: int, person: Person, committee_id: int,
                            person_committee_id: int, person_committees_cnt: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button(
        "🔄 Изменить 🔄",
        MenuCallback(level=level + 1, menu_name=MenuName.UPDATE_PERSON_COMMITTEE, person_id=person.id,
                     committee_id=committee_id,
                     current_person_committee_id=person_committee_id)
    ))

    if person_committees_cnt > 1:
        kb.row(_create_inline_button(
            "❌ Удалить ❌",
            MenuCallback(level=level, menu_name=MenuName.CONFIRM_DELETE_PERSON_COMMITTEE, person_id=person.id,
                         committee_id=committee_id, current_person_committee_id=person_committee_id)
        ))

    kb.row(_create_back_button(level, MenuName.PERSON, person_id=person.id, committee_id=committee_id))

    return kb.as_markup()


def get_delete_person_kb(level: int, person_id: int, committee_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(_create_inline_button(
        "✅ Подтвердить ✅",
        MenuCallback(level=level, menu_name=MenuName.CONFIRM_DELETE_PERSON, person_id=person_id,
                     committee_id=committee_id)
    ))

    kb.row(_create_back_button(level, MenuName.PERSON, committee_id=committee_id, person_id=person_id))

    return kb.as_markup()


def get_add_person_committee_kb(level: int, committee_id: int, person: Person,
                                committees: list[Committee]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    person_committee = person.committees[0]

    for com in committees:
        if not com.name == person_committee.name:
            kb.add(_create_inline_button(
                f"{com.talisman} {com.name} {com.talisman}",
                MenuCallback(level=level, menu_name=MenuName.CONFIRM_ADD_PERSON_COMMITTEE, committee_id=committee_id,
                             person_id=person.id, new_person_committee_id=com.id)
            ))
    kb.adjust(2)

    kb.row(_create_back_button(level, MenuName.PERSON, person_id=person.id, committee_id=committee_id))

    return kb.as_markup()


def get_points_in_category_kb(
        level: int,
        menu_name: MenuName,
        person_id: int,
        committee_id: int,
        category_id: int,
        current_points: int,
        old_points: int
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.row(
        _create_inline_button(
            "⏪",
            MenuCallback(level=level, menu_name=menu_name, person_id=person_id, category_id=category_id,
                         current_points=current_points,
                         edit_points=-5, committee_id=committee_id, old_points=old_points)
        ),
        _create_inline_button(
            "◀️",
            MenuCallback(level=level, menu_name=menu_name, person_id=person_id, category_id=category_id,
                         current_points=current_points,
                         edit_points=-1, committee_id=committee_id, old_points=old_points)
        ),
        InlineKeyboardButton(text=str(current_points), callback_data="#"),
        _create_inline_button(
            "▶️",
            MenuCallback(level=level, menu_name=menu_name, person_id=person_id, category_id=category_id,
                         current_points=current_points,
                         edit_points=1, committee_id=committee_id, old_points=old_points)
        ),
        _create_inline_button(
            "⏩",
            MenuCallback(level=level, menu_name=menu_name, person_id=person_id, category_id=category_id,
                         current_points=current_points,
                         edit_points=5, committee_id=committee_id, old_points=old_points)
        )
    )

    kb.row(
        _create_inline_button(
            "🔄 Сброс 🔄",
            MenuCallback(level=level, menu_name=menu_name, person_id=person_id, category_id=category_id,
                         current_points=old_points, committee_id=committee_id, old_points=old_points)
        ),
        _create_inline_button(
            "💬 Комментарий 💬",
            MenuCallback(level=level + 1, menu_name=MenuName.COMMENT_FOR_UPDATE_POINTS, person_id=person_id,
                         category_id=category_id, current_points=current_points, committee_id=committee_id,
                         old_points=old_points)
        )
    )

    kb.row(_create_back_button(level, MenuName.PERSON_POINTS, person_id=person_id, committee_id=committee_id))

    return kb.as_markup()


def get_comment_for_update_points_kb(
        level: int,
        person_id: int,
        committee_id: int,
        category_id: int,
        current_points: int,
        old_points: int,
        comment: str | None,
        current_state: str
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if current_state == "UpdatePersonPoints:comment" and comment:
        kb.row(
            _create_inline_button(
                "✅ Подтвердить ✅",
                MenuCallback(level=level, menu_name=MenuName.CONFIRM_UPDATE_PERSON_POINTS, person_id=person_id,
                             category_id=category_id, current_points=current_points, committee_id=committee_id,
                             old_points=old_points)
            )
        )

    kb.row(_create_back_button(level, MenuName.POINTS_IN_CATEGORY, person_id=person_id, committee_id=committee_id,
                               category_id=category_id,
                               current_points=current_points, old_points=old_points))

    return kb.as_markup()


def get_update_person_committee_kb(
        level: int,
        person: Person,
        committee_id: int,
        current_person_committee: Committee,
        committees: list[Committee]
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    for committee in committees:
        if committee.name not in [person_committee.name for person_committee in person.committees]:
            kb.add(
                _create_inline_button(
                    f"{committee.talisman} {committee.name} {committee.talisman}",
                    MenuCallback(level=level, menu_name=MenuName.CONFIRM_UPDATE_PERSON_COMMITTEE, person_id=person.id,
                                 committee_id=committee_id, current_person_committee_id=current_person_committee.id,
                                 new_person_committee_id=committee.id)
                )
            )
    kb.adjust(2)

    kb.row(_create_back_button(level, MenuName.PERSON_COMMITTEE, person_id=person.id,
                               current_person_committee_id=current_person_committee.id,
                               committee_id=committee_id))

    return kb.as_markup()
