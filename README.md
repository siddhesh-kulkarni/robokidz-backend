# Backend – RoboKidz Quiz Generator

FastAPI API that validates lesson input, generates a 5-question MCQ quiz (Groq or mock), and saves it in Postgres.

## Folder structure (open-source FastAPI style)

```
robokidz-backend/
  app/
    main.py                   # HTTP routes
    schemas.py                # Pydantic request validation
    database/database.py      # engine, SessionLocal, get_db
    models/models.py          # quiz_master + questions tables
    services/ai_model_llm.py  # Groq / MOCK_LLM quiz generation
  tests/
    conftest.py               # test DB + client fixture
    test_quizzes.py           # API tests
  .env.example
  requirements.txt
```

- `main.py` – routes only  
- `schemas.py` – input validation  
- `models/` – DB tables  
- `database/` – connection + session  
- `services/` – LLM logic (not in routes)  
- `tests/` – isolated from real Postgres / Groq  

## Setup & run

```bash
cd robokidz-backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
# source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
MOCK_LLM=true
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

| Setting | Meaning |
|---------|---------|
| `MOCK_LLM=true` | Fixed sample quiz, no Groq key needed |
| `MOCK_LLM=false` | Real AI generation (needs `GROQ_API_KEY`) |

Start server:

```bash
uvicorn app.main:app --reload --port 8000
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  

## How to test

### Automated (pytest)

```bash
cd robokidz-backend
venv\Scripts\activate
pytest -q
```

What tests do:

- Use **in-memory SQLite** (`sqlite:///:memory:`) – not your real Postgres  
- Force **`MOCK_LLM=true`** – no Groq call  
- Cover short/long lesson rejection, create + get quiz, list newest-first  

### Manual (Swagger)

1. Open http://127.0.0.1:8000/docs  
2. `POST /api/quizzes` with title, lesson (≥50 chars), age 8–14  
3. `GET /api/quizzes` – see new quiz in list  
4. `GET /api/quizzes/{id}` – see 5 questions  

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/quizzes` | Generate + save quiz |
| GET | `/api/quizzes?page=1&size=10` | List active quizzes (newest first) |
| GET | `/api/quizzes/{id}` | One quiz with questions |

Create body:

```json
{
  "title": "Parts of a Plant",
  "lesson_text": ".... at least 50 chars ....",
  "age": 10
}
```

Validation:

- lesson text: 50–5000 characters  
- age: 8–14  
- LLM/mock output: exactly 5 questions, each with 4 unique options and 1 correct answer in options  

## Code flow

```
POST /api/quizzes
  → schemas.QuizCreate (validate input)
  → generate_quiz() in ai_model_llm.py (Groq or mock)
  → validate_questions() (never trust model blindly)
  → save QuizMaster + QuizQuestionMappingMaster
  → return quiz_id
```

## Where AI is used (product)

**File:** `app/services/ai_model_llm.py`

- If `MOCK_LLM=false` → calls **Groq** chat completions with a system prompt (5 MCQs, kids language, lesson-only, JSON)  
- If `MOCK_LLM=true` → returns fixed `MOCK_QUESTIONS` (still validated + saved)  
- Frontend never talks to Groq — only this API  

## Where I used AI coding tools

I used ChatGPT / VS Code Copilot while building the backend. Main places:

1. FastAPI folder layout / scaffolding ideas  
2. SQLAlchemy `engine` / `SessionLocal` / `get_db` wiring  
3. Groq request shape + JSON parsing  
4. pytest `TestClient` + DB dependency override  
5. README wording  

I reviewed and edited the final code myself. The **quiz rules in `SYSTEM_PROMPT`** are product decisions and were kept intentional.

## Design decisions

- FastAPI + SQLAlchemy – simple, matches task preference  
- Postgres via `DATABASE_URL` – Neon or local  
- `MOCK_LLM` – run/tests without API key  
- Two tables – `quiz_master` + `quiz_questions_mapping_master`  
- Validate LLM output before `commit`  
- Soft hide with `is_active`  

## What I would improve later

- `{ items, total }` for pagination UI  
- Retry once if LLM returns bad JSON  
- Alembic migrations instead of `create_all`  
- Teacher auth  
- Docker + CI  

## Notes

- Do not commit `.env` or API keys — only `.env.example`  
- CORS allows `http://localhost:3000`  
- Frontend README: `../robokidz-frontend/README.md`  
