from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EventRegistrationTable(Base):
    __tablename__ = "event_registration_tables"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    table_url: Mapped[str] = mapped_column(unique=True)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_types.id", ondelete="CASCADE"))

    event_type: Mapped["EventType"] = relationship("EventType", back_populates="tables")
    persons: Mapped[list["EventRegistrationTablePerson"]] = relationship(
        "EventRegistrationTablePerson",
        back_populates="table"
    )
