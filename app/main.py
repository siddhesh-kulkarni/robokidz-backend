import logging

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.database import Base, engine, get_db
from app.models import models
from app.schemas import QuizCreate
from app.services.ai_model_llm import generate_quiz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Robokidz Quiz Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def validate_questions(questions):
    if not isinstance(questions, list) or len(questions) != 5:
        raise ValueError("Exactly 5 questions are required")

    for question in questions:
        options = question.get("options", [])
        answer = question.get("correct_answer")
        if (
            not question.get("question_text")
            or not isinstance(options, list)
            or len(options) != 4
            or len(set(options)) != 4
            or answer not in options
        ):
            raise ValueError("Invalid question or options from LLM")


@app.get("/")
def root():
    return {"message": "Robokidz Quiz Generator API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/quizzes")
def create_quiz(data: QuizCreate, db: Session = Depends(get_db)): # This is the endpoint to create a quiz
    try: 
        questions = generate_quiz(data.lesson_text, data.age) # This is the function to generate the quiz
        validate_questions(questions) # This is the function to validate the quiz

        quiz = models.QuizMaster( # This is the model to create a quiz
            title=data.title.strip(),
            lesson_text=data.lesson_text,
            age=data.age,
        )
        db.add(quiz) # This is the function to add the quiz to the database
        db.flush() # This is the function to flush the quiz to the database

        for question in questions:
            db.add(
                models.QuizQuestionMappingMaster(
                    quiz_id=quiz.id,
                    question_text=question["question_text"],
                    options=question["options"],
                    correct_answer=question["correct_answer"],
                )
            )

        db.commit()
        db.refresh(quiz)

        return {
            "message": "Quiz created successfully",
            "quiz_id": quiz.id,
            "title": quiz.title,
            "total_questions": len(questions),
        }
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        db.rollback()
        logger.exception("Failed to create quiz")
        raise HTTPException(status_code=500, detail="Failed to create quiz")


@app.get("/api/quizzes")
def get_quizzes(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    quizzes = (
        db.query(models.QuizMaster)
        .filter(models.QuizMaster.is_active == True)
        .order_by(
            models.QuizMaster.created_at.desc(),
            models.QuizMaster.id.desc(),
        )
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return [
        {
            "id": quiz.id,
            "title": quiz.title,
            "created_at": quiz.created_at,
        }
        for quiz in quizzes
    ]


@app.get("/api/quizzes/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = (
        db.query(models.QuizMaster)
        .filter(models.QuizMaster.id == quiz_id, models.QuizMaster.is_active == True)
        .first()
    )

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = (
        db.query(models.QuizQuestionMappingMaster)
        .filter(models.QuizQuestionMappingMaster.quiz_id == quiz_id)
        .all()
    )

    return {
        "id": quiz.id,
        "title": quiz.title,
        "lesson_text": quiz.lesson_text,
        "age": quiz.age,
        "created_at": quiz.created_at,
        "updated_at": quiz.updated_at,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "options": q.options,
                "correct_answer": q.correct_answer,
            }
            for q in questions
        ],
    }
