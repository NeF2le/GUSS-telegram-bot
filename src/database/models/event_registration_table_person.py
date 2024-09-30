from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EventRegistrationTablePerson(Base):
    __tablename__ = "event_registration_table_persons"
    __table_args__ = (UniqueConstraint('full_name', 'table_id', name='_full_name_table_uc'),)


    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str]
    matched_person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    points_added: Mapped[bool] = mapped_column(default=False)
    table_id: Mapped[int] = mapped_column(
        ForeignKey("event_registration_tables.id", ondelete="CASCADE"), index=True)

    table: Mapped["EventRegistrationTable"] = relationship("EventRegistrationTable",
                                                           back_populates="persons")
    person: Mapped["Person"] = relationship("Person", back_populates="table_persons")
