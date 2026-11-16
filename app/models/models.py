
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
)

from app.database.database import Base


class QuizMaster(Base):
    __tablename__ = "quiz_master"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    lesson_text = Column(Text, nullable=False)
    age = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions_mapping_master"

    id = Column(Integer, primary_key=True, index=True)

    quiz_id = Column(
        Integer,
        ForeignKey("quiz_master.id"),
        nullable=False,
    )

    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(500), nullable=False)
