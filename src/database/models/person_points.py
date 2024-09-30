from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import Base


class PersonPoints(Base):
    __tablename__ = "person_points"

    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    points_value: Mapped[int] = mapped_column(default=0)

    person: Mapped["Person"] = relationship("Person", back_populates="points")
    category: Mapped["Category"] = relationship("Category", back_populates="persons_points")

    @validates('points_value')
    def validate_points_value(self, key, value):
        if value < 0:
            return 0
        return value
