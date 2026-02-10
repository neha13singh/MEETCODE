from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.question import Question, TestCase, CodeTemplate
from app.schemas.question import Question as QuestionSchema, QuestionCreate, QuestionList
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[QuestionList])
async def read_questions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    difficulty: Optional[str] = None,
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Retrieve questions.
    """
    query = select(Question)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    questions = result.scalars().all()

    # If user is logged in, check solved status
    solved_question_ids = set()
    if current_user:
        from app.models.submission import Submission
        sub_query = (
            select(Submission.question_id)
            .where(
                Submission.user_id == current_user.id,
                Submission.status == "accepted"
            )
        )
        sub_result = await db.execute(sub_query)
        solved_question_ids = set(sub_result.scalars().all())

    # Map to schema with is_solved
    question_list = []
    for q in questions:
        q_data = QuestionList.from_orm(q)
        q_data.is_solved = q.id in solved_question_ids
        question_list.append(q_data)
        
    return question_list

@router.post("/", response_model=QuestionSchema)
async def create_question(
    *,
    db: AsyncSession = Depends(get_db),
    question_in: QuestionCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new question.
    """
    # Create question
    question = Question(
        title=question_in.title,
        slug=question_in.slug,
        description=question_in.description,
        difficulty=question_in.difficulty,
        avg_solve_time=question_in.avg_solve_time,
        tags=question_in.tags,
        constraints=question_in.constraints,
        examples=question_in.examples
    )
    db.add(question)
    await db.flush()  # to get ID

    # Create test cases
    for tc in question_in.test_cases:
        test_case = TestCase(
            question_id=question.id,
            input=tc.input,
            expected_output=tc.expected_output,
            is_hidden=tc.is_hidden,
            is_sample=tc.is_sample,
            execution_order=tc.execution_order
        )
        db.add(test_case)

    # Create templates
    for tmpl in question_in.templates:
        template = CodeTemplate(
            question_id=question.id,
            language=tmpl.language,
            template_code=tmpl.template_code,
            starter_code=tmpl.starter_code
        )
        db.add(template)

    await db.commit()
    await db.refresh(question)
    
    # Reload with relationships
    query = select(Question).where(Question.id == question.id).options(
        selectinload(Question.test_cases),
        selectinload(Question.templates)
    )
    result = await db.execute(query)
    return result.scalars().first()

@router.get("/{slug}", response_model=QuestionSchema)
async def read_question(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get question by slug.
    """
    query = select(Question).where(Question.slug == slug).options(
        selectinload(Question.test_cases),
        selectinload(Question.templates)
    )
    result = await db.execute(query)
    question = result.scalars().first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
        
    return question
