from sqlalchemy import String, JSON, TIMESTAMP, func, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.enums import ActionType


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_type: Mapped[ActionType]
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    old_data: Mapped[dict | None] = mapped_column(JSON)
    new_data: Mapped[dict | None] = mapped_column(JSON)
    comment: Mapped[str | None] = mapped_column(Text)
    changed_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    changed_by: Mapped[str] = mapped_column(String(100))

    person: Mapped["Person"] = relationship("Person", back_populates="audit_logs")
