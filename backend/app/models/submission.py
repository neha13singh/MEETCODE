from sqlalchemy import String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid
from datetime import datetime
from typing import Optional

class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_participant_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("match_participants.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    submission_type: Mapped[str] = mapped_column(String(10)) # run, submit
    status: Mapped[Optional[str]] = mapped_column(String(20), index=True) # pending, running, accepted, etc.
    test_cases_passed: Mapped[Optional[int]] = mapped_column(Integer)
    total_test_cases: Mapped[Optional[int]] = mapped_column(Integer)
    execution_time: Mapped[Optional[int]] = mapped_column(Integer)
    memory_used: Mapped[Optional[int]] = mapped_column(Integer)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
    question: Mapped["Question"] = relationship()
    match_participant: Mapped["MatchParticipant"] = relationship()
