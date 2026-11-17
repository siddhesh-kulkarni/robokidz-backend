from pydantic import BaseModel, Field, field_validator


class QuizCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    lesson_text: str
    age: int = Field(..., ge=8, le=14)

    @field_validator("lesson_text")
    @classmethod
    def check_lesson_length(cls, value: str) -> str:
        text = value.strip()
        if len(text) < 50:
            raise ValueError("Lesson text must be at least 50 characters")
        if len(text) > 5000:
            raise ValueError("Lesson text cannot be more than 5000 characters")
        return text
