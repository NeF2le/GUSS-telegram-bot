from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class VkActivity(Base):
    __tablename__ = "vk_activities"

    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), primary_key=True)
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)

    person: Mapped["Person"] = relationship("Person", back_populates="vk_activities")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="vk_activities")
    post: Mapped["Post"] = relationship("Post", back_populates="vk_activities")
