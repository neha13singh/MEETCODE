from sqlalchemy import String, Integer, Text, Boolean, Numeric, ForeignKey, ForeignKeyConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid
from datetime import datetime
from typing import List, Optional

class Question(Base):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(10), index=True) # easy, medium, hard
    avg_solve_time: Mapped[int] = mapped_column(Integer, nullable=False) # seconds
    acceptance_rate: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    constraints: Mapped[Optional[str]] = mapped_column(Text)
    examples: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    
    test_cases: Mapped[List["TestCase"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    templates: Mapped[List["CodeTemplate"]] = relationship(back_populates="question", cascade="all, delete-orphan")
    matches: Mapped[List["Match"]] = relationship(back_populates="question")

class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False)
    execution_order: Mapped[Optional[int]] = mapped_column(Integer)

    question: Mapped["Question"] = relationship(back_populates="test_cases")

class CodeTemplate(Base):
    __tablename__ = "code_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))
    language: Mapped[str] = mapped_column(String(20), nullable=False)
    template_code: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[Optional[str]] = mapped_column(Text)
    
    question: Mapped["Question"] = relationship(back_populates="templates")
