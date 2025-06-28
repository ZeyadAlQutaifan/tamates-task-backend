# routers/questions_router.py
from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from main import get_db
from schemas.questions_schemas import QuestionBase
from modles.question_modles import  Question, Choices

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
)


db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/")
def create_question(
    question: QuestionBase,
    db: db_dependency
):
    db_question = Question(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()

    return {"message": "Question created successfully", "question_id": db_question.id}


@router.get("/choices")
async def get_choices(question_id: int, db: db_dependency):
    choices = db.query(Choices).filter_by(question_id=question_id).all()
    if not choices:
        raise HTTPException(status_code=404, detail="No choices found")
    return {"choices": choices}


@router.get("/{question_id}")
async def get_question(question_id: int, db: db_dependency):
    result = db.query(Question).get(question_id)
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result
