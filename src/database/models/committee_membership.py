from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CommitteeMembership(Base):
    __tablename__ = "committee_membership"

    person_id: Mapped[int] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True
    )
    committee_id: Mapped[int] = mapped_column(
        ForeignKey("committees.id", ondelete="CASCADE"),
        primary_key=True
    )
