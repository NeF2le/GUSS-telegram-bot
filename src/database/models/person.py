from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from .base import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    vk_id: Mapped[int] = mapped_column(unique=True)

    committees: Mapped[list["Committee"]] = relationship(
        "Committee",
        back_populates="persons",
        secondary="committee_membership",
        lazy="selectin"
    )
    vk_activities: Mapped[list["VkActivity"]] = relationship(
        "VkActivity",
        back_populates="person"
    )
    points: Mapped[list["PersonPoints"]] = relationship(
        "PersonPoints",
        back_populates="person",
        lazy="selectin"
    )
