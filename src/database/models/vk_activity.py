from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from src.enums import ActivityType


class VkActivity(Base):
    __tablename__ = "vk_activities"
    __table_args__ = (UniqueConstraint('person_id', 'post_url', 'activity_type', name='_person_post_activity_uc'),)

    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True)
    post_url: Mapped[str] = mapped_column(primary_key=True)
    activity_type: Mapped[ActivityType] = mapped_column(primary_key=True)

    person: Mapped["Person"] = relationship("Person", back_populates="vk_activities")
