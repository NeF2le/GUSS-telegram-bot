from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class PersonPoints(Base):
    __tablename__ = "person_points"

    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, default=0)
