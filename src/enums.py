from enum import Enum


class ActivityType(Enum):
    VK_LIKE = 'vk_like'
    VK_COMMENT = 'vk_comment'


class DocumentType(Enum):
    PROTOCOL = 'protocol'
    EVENT_REGISTRATION_TABLE = 'event_registration_table'


class ActionType(Enum):
    INSERT_PERSON = 'Добавление человека'
    DELETE_PERSON = 'Удаление человека'
    INSERT_MEMBERSHIP = 'Добавление комитета'
    UPDATE_MEMBERSHIP = 'Изменение комитета'
    DELETE_MEMBERSHIP = 'Удаление комитета'
    UPDATE_PERSON_POINTS = 'Изменение баллов'
    UPDATE_PERSON_FIRST_NAME = 'Изменение имени'
    UPDATE_PERSON_LAST_NAME = 'Изменение фамилии'


class MenuName(Enum):
    START = 'start'
    EVENT_REGISTRATION_TABLES_MAIN = 'reg_tables_main'
    EVENT_REGISTRATION_TABLE = 'reg_table'
    EVENT_REGISTRATION_TABLES = 'reg_tables'
    ADD_EVENT_REGISTRATION_TABLE = 'add_reg_table'
    SELECT_EVENT_TYPE = 'select_event_type'
    ADD_PERSON = 'add_person'
    SELECT_COMMITTEE = 'select_committee'
    UPDATE_FIRST_NAME = 'update_first_name'
    UPDATE_LAST_NAME = 'update_last_name'
    COMMENT_FOR_UPDATE_POINTS = 'comment_for_update_points'
    CONFIRM_ADD_PERSON = 'confirm_add_person'
    CONFIRM_ADD_EVENT_REGISTRATION_TABLE = 'confirm_add_reg_table'
    CONFIRM_ADD_EVENT_ATTENDANCE_POINTS = 'add_event_attendance_points'
    CONFIRM_UPDATE_FIRST_NAME = 'confirm_update_first_name'
    CONFIRM_UPDATE_LAST_NAME = 'confirm_update_last_name'
    ADD_COMMITTEE_ATTENDANCE_POINTS = 'add_committee_attendance_points'
    ADD_EVENT_ATTENDANCE_POINTS = 'add_event_attendance_points'
    CONFIRM_DELETE_PERSON = 'confirm_delete_person'
    CONFIRM_ADD_PERSON_COMMITTEE = 'confirm_add_person_committee'
    POINTS_IN_CATEGORY = 'points_in_category'
    CONFIRM_UPDATE_PERSON_POINTS = 'confirm_update_person_points'
    CONFIRM_UPDATE_PERSON_COMMITTEE = 'confirm_update_person_committee'
    CONFIRM_DELETE_PERSON_COMMITTEE = 'confirm_delete_person_committee'
    PERSON = 'person'
    DELETE_PERSON = 'delete_person'
    PERSON_COMMITTEE = 'person_committee'
    UPDATE_PERSON_COMMITTEE = 'update_person_committee'
    ADD_PERSON_COMMITTEE = 'add_person_committee'
    COMMITTEE_PROTOCOLS = 'committee_protocols'
    COMMITTEE_MEMBERS = 'committee_members'
    COMMITTEE = 'committee'
    PROTOCOL = 'protocol'
    PERSON_POINTS = 'person_points'
