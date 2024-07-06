from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    vk_id: Mapped[int] = mapped_column(Integer)

    committees: Mapped[list["Committee"]] = relationship(
        "Committee",
        back_populates="members",
        secondary="committee_membership"
    )
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="persons",
        secondary="vk_activities"
    )
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="persons",
        secondary="person_points"
    )
