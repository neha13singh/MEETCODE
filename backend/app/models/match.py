from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid
from datetime import datetime
from typing import List, Optional

class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("questions.id"))
    mode: Mapped[str] = mapped_column(String(20)) # practice, competitive
    difficulty: Mapped[Optional[str]] = mapped_column(String(10))
    max_time: Mapped[int] = mapped_column(Integer, nullable=False) # seconds
    status: Mapped[str] = mapped_column(String(20), default="waiting", index=True) # waiting, active, completed, timeout
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    winner_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    question: Mapped["Question"] = relationship(back_populates="matches")
    participants: Mapped[List["MatchParticipant"]] = relationship(back_populates="match", cascade="all, delete-orphan")
    winner: Mapped["User"] = relationship()

class MatchParticipant(Base):
    __tablename__ = "match_participants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    result: Mapped[Optional[str]] = mapped_column(String(20)) # win, lose, timeout, practice_complete
    solution_code: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[Optional[str]] = mapped_column(String(20))
    execution_time: Mapped[Optional[int]] = mapped_column(Integer) # ms
    memory_used: Mapped[Optional[int]] = mapped_column(Integer) # KB
    test_cases_passed: Mapped[Optional[int]] = mapped_column(Integer)
    total_test_cases: Mapped[Optional[int]] = mapped_column(Integer)

    match: Mapped["Match"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship()
