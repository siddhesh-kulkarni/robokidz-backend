import json
import logging
import os
import random

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

# Rules for LLM Model
SYSTEM_PROMPT = """
You are an educational quiz generator for children.

Rules:
1. Generate exactly 5 different multiple-choice questions.
2. Each question must have exactly 4 options.
3. Each question must have exactly one correct answer.
4. Questions must be suitable for the student's age.
5. Use information ONLY from the provided lesson.
6. Do not invent facts or introduce unrelated general knowledge.
7. Use simple and understandable language.
8. All incorrect options must be plausible and related to the lesson.
9. Avoid repeating questions.
10. The correct_answer must exactly match one of the four options.
11. Distribute correct answers across positions A, B, C, and D.
12. Do not always put the correct answer in the first position.

Return valid JSON only.
Do not include Markdown or explanations.
"""
# Fixed sample used when MOCK_LLM=true (no API call)
MOCK_QUESTIONS = [
    {
        "question_text": "What do plants need to grow?",
        "options": ["Sunlight, water and soil", "Only rocks", "Only wind", "Only plastic"],
        "correct_answer": "Sunlight, water and soil",
    },
    {
        "question_text": "Which part helps a plant make food?",
        "options": ["Leaves", "Rocks", "Clouds", "Sand"],
        "correct_answer": "Leaves",
    },
    {
        "question_text": "What do roots take from the soil?",
        "options": ["Water", "Fire", "Airplanes", "Books"],
        "correct_answer": "Water",
    },
    {
        "question_text": "What helps the plant stand upright?",
        "options": ["The stem", "The moon", "A chair", "A car"],
        "correct_answer": "The stem",
    },
    {
        "question_text": "Which of these is needed by plants?",
        "options": ["Soil", "Television", "Shoes", "Phones"],
        "correct_answer": "Soil",
    },
]



def generate_quiz(lesson_text: str, age: int):
    #test mode no Groq call
    if os.getenv("MOCK_LLM", "false").lower() == "true":
        logger.info("MOCK_LLM=true – returning sample quiz for age %s", age)
        questions = [dict(q) for q in MOCK_QUESTIONS]
        for question in questions:
            random.shuffle(question["options"])
        return questions

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing. Set it in .env or use MOCK_LLM=true")

    ai_model = Groq(api_key=api_key)

    try:
        logger.info("Generating quiz for age %s", age)

        response = ai_model.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            messages=[
                {
                    "role": "system",           # System role is the role of the model that is generating the quiz
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",             # User role is the role of the user that is requesting the quiz
                    "content": f"""
                    Age: {age}

                    Lesson:
                    {lesson_text}

                    Return in this format:    
                    {{
                        "questions": [
                            {{
                                "question_text": "Question",
                                "options": ["A", "B", "C", "D"],
                                "correct_answer": "A"
                            }}
                        ]
                    }}
                    """,                       # This is the format of the quiz that the model will return
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2, # Temperature means the model's creativity or randomness in generating the quiz it can be 0.0 to 1.0
        )

        result = json.loads(response.choices[0].message.content)
        questions = result["questions"]

        for question in questions:
            random.shuffle(question["options"])   # This is to shufle the options of the quiz so that the correct answer is not always in the first position

        logger.info("Quiz generated successfully")
        return questions

    except Exception:
        logger.exception("Quiz generation failed")
        raise
