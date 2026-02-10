from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

class SubmissionBase(BaseModel):
    language: str
    code: str
    question_id: UUID

class SubmissionCreate(SubmissionBase):
    match_id: Optional[UUID] = None

class SubmissionRun(SubmissionBase):
    """Payload for running code against sample test cases"""
    pass

class SubmissionResult(BaseModel):
    status: str # 'accepted', 'wrong_answer', etc.
    test_cases_passed: int
    total_test_cases: int
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[List[Any]] = None # Detailed results per test case

class SubmissionResponse(SubmissionResult):
    id: UUID
    created_at: datetime
    code: str
    language: str
    
    class Config:
        from_attributes = True
