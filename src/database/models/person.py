from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    vk_id: Mapped[int] = mapped_column(unique=True)

    committees: Mapped[list["Committee"]] = relationship(
        "Committee",
        back_populates="persons",
        secondary="memberships"
    )
    vk_activities: Mapped[list["VkActivity"]] = relationship(
        "VkActivity",
        back_populates="person"
    )
    points: Mapped[list["PersonPoints"]] = relationship(
        "PersonPoints",
        back_populates="person"
    )
    protocol_persons: Mapped[list["ProtocolPerson"]] = relationship(
        "ProtocolPerson",
        back_populates="person"
    )
    table_persons: Mapped[list["EventRegistrationTablePersons"]] = relationship(
        "EventRegistrationTablePerson",
        back_populates="person"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="person"
    )
