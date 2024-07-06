from sqlalchemy import String, JSON, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_log_id: Mapped[int] = mapped_column(primary_key=True)
    action_type: Mapped[str] = mapped_column(String(50))
    table_name: Mapped[str] = mapped_column(String(50))
    old_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    new_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    changed_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    changed_by: Mapped[str] = mapped_column(String(100))
