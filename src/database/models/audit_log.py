from sqlalchemy import String, JSON, TIMESTAMP, func, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
import enum


class ActionType(enum.Enum):
    INSERT_PERSON = 'Добавление человека'
    DELETE_PERSON = 'Удаление человека'
    INSERT_MEMBERSHIP = 'Добавление комитета человеку'
    UPDATE_MEMBERSHIP = 'Обновление комитета у человека'
    DELETE_MEMBERSHIP = 'Удаление комитета у человека'
    INSERT_VK_ACTIVITY = 'Добавление ВК активности человеку'
    UPDATE_PERSON_POINTS = 'Изменение баллов у человека'


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_type: Mapped[ActionType]
    table_name: Mapped[str]
    old_data: Mapped[dict | None] = mapped_column(JSON)
    new_data: Mapped[dict | None] = mapped_column(JSON)
    changed_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    comment: Mapped[str | None] = mapped_column(Text)
    changed_by: Mapped[str] = mapped_column(String(100))
