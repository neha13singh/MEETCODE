import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base_class import Base


class PointAward(Base):
    """Immutable ledger of points awarded to users.

    The unique constraint makes awards idempotent: the same win or the same
    first-time practice solve can never be rewarded twice, even if two
    requests race.
    """

    __tablename__ = "point_awards"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "reason",
            "reference_id",
            name="uq_point_award_user_reason_reference",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(30), nullable=False)  # match_win, practice_solve
    reference_id: Mapped[uuid.UUID] = mapped_column(nullable=False)  # match id or question id
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
