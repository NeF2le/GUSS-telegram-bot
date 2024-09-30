from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)

    persons_points: Mapped[list["PersonPoints"]] = relationship(
        "PersonPoints",
        back_populates="category"
    )

