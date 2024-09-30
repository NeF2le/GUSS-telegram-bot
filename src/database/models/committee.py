from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Committee(Base):
    __tablename__ = "committees"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    talisman: Mapped[str] = mapped_column(Text, unique=True)
    protocols_document_id: Mapped[str] = mapped_column(unique=True)

    persons: Mapped[list["Person"]] = relationship(
        "Person",
        back_populates="committees",
        secondary="memberships"
    )

    protocols: Mapped[list["Protocol"]] = relationship(
        "Protocol",
        back_populates="committee"
    )
