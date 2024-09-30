from sqlalchemy import ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base


class Protocol(Base):
    __tablename__ = "protocols"
    __table_args__ = (UniqueConstraint('number', 'date', 'committee_id', name='_number_date_committee_uc'),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    number: Mapped[int]
    date: Mapped[datetime] = mapped_column(Date())
    committee_id: Mapped[int] = mapped_column(ForeignKey("committees.id", ondelete="CASCADE"))

    committee: Mapped["Committee"] = relationship("Committee", back_populates="protocols")
    persons: Mapped[list["ProtocolPerson"]] = relationship("ProtocolPerson", back_populates="protocol")
