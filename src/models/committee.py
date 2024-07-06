from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Committee(Base):
    __tablename__ = "committees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    members: Mapped[list["Person"]] = relationship(
        "Person",
        back_populates="committees",
        secondary="committee_membership"
    )
