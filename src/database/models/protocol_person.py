from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProtocolPerson(Base):
    __tablename__ = "protocol_persons"
    __table_args__ = (UniqueConstraint('full_name', 'protocol_id', name='_first_last_protocol_uc'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str]
    matched_person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="SET NULL"), nullable=True)
    points_added: Mapped[bool] = mapped_column(default=False)
    protocol_id: Mapped[int] = mapped_column(ForeignKey("protocols.id", ondelete="CASCADE"), index=True)

    protocol: Mapped["Protocol"] = relationship("Protocol", back_populates="persons")
    person: Mapped["Person"] = relationship("Person", back_populates="protocol_persons")
