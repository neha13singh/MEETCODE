from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.schemas.question import Question

class MatchBase(BaseModel):
    mode: str
    difficulty: Optional[str] = None
    max_time: int
    status: str

class MatchCreate(BaseModel):
    mode: str
    difficulty: Optional[str] = None
    question_id: Optional[UUID] = None

class MatchParticipantSchema(BaseModel):
    id: UUID
    user_id: UUID
    result: Optional[str] = None
    execution_time: Optional[int] = None
    test_cases_passed: Optional[int] = None
    total_test_cases: Optional[int] = None
    joined_at: datetime
    
    class Config:
        from_attributes = True

class Match(MatchBase):
    id: UUID
    question_id: Optional[UUID]
    started_at: Optional[datetime]
    started_at_ts: Optional[float] = None # Epoch timestamp in ms
    completed_at: Optional[datetime]
    winner_id: Optional[UUID]
    created_at: datetime
    
    participants: List[MatchParticipantSchema] = []
    question: Optional[Question] = None

    class Config:
        from_attributes = True
