from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

# Test Case Schemas
class TestCaseBase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False
    is_sample: bool = False
    execution_order: Optional[int] = None

class TestCaseCreate(TestCaseBase):
    pass

class TestCase(TestCaseBase):
    id: UUID
    question_id: UUID

    class Config:
        from_attributes = True

# Code Template Schemas
class CodeTemplateBase(BaseModel):
    language: str
    template_code: str
    starter_code: Optional[str] = None

class CodeTemplateCreate(CodeTemplateBase):
    pass

class CodeTemplate(CodeTemplateBase):
    id: UUID
    question_id: UUID

    class Config:
        from_attributes = True

# Question Schemas
class QuestionBase(BaseModel):
    title: str
    slug: str
    description: str
    difficulty: str  # easy, medium, hard
    avg_solve_time: int
    tags: Optional[Dict[str, Any]] = None
    constraints: Optional[str] = None
    examples: Optional[List[Dict[str, Any]]] = None

class QuestionCreate(QuestionBase):
    test_cases: List[TestCaseCreate]
    templates: List[CodeTemplateCreate]

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    avg_solve_time: Optional[int] = None
    tags: Optional[Dict[str, Any]] = None
    constraints: Optional[str] = None

class Question(QuestionBase):
    id: UUID
    created_at: datetime
    test_cases: List[TestCase] = []
    templates: List[CodeTemplate] = []

    class Config:
        from_attributes = True

class QuestionList(BaseModel):
    id: UUID
    title: str
    slug: str
    difficulty: str
    avg_solve_time: int
    acceptance_rate: Optional[float] = None
    tags: Optional[Dict[str, Any]] = None
    is_solved: bool = False

    class Config:
        from_attributes = True
