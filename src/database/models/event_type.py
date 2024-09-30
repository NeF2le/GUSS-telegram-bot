from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class EventType(Base):
    __tablename__ = "event_types"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    points: Mapped[int] = mapped_column(default=0)

    tables: Mapped[list["EventRegistrationTable"]] = relationship(
        "EventRegistrationTable",
        back_populates="event_type"
    )

