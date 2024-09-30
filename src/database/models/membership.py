from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Membership(Base):
    __tablename__ = "memberships"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True
    )
    committee_id: Mapped[int] = mapped_column(
        ForeignKey("committees.id", ondelete="CASCADE"),
        primary_key=True
    )
