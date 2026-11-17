from tests.conftest import SAMPLE_LESSON


def test_reject_short_lesson(client):
    response = client.post(
        "/api/quizzes",
        json={
            "title": "Too Short",
            "lesson_text": "short text",
            "age": 10,
        },
    )
    assert response.status_code == 422


def test_reject_long_lesson(client):
    response = client.post(
        "/api/quizzes",
        json={
            "title": "Too Long",
            "lesson_text": "x" * 5001,
            "age": 10,
        },
    )
    assert response.status_code == 422


def test_create_and_get_quiz(client):
    create_res = client.post(
        "/api/quizzes",
        json={
            "title": "Plant Basics",
            "lesson_text": SAMPLE_LESSON,
            "age": 10,
        },
    )
    assert create_res.status_code == 200
    data = create_res.json()
    assert data["total_questions"] == 5
    quiz_id = data["quiz_id"]

    detail_res = client.get(f"/api/quizzes/{quiz_id}")
    assert detail_res.status_code == 200
    quiz = detail_res.json()
    assert quiz["title"] == "Plant Basics"
    assert len(quiz["questions"]) == 5

    for question in quiz["questions"]:
        assert len(question["options"]) == 4
        assert question["correct_answer"] in question["options"]


def test_list_quizzes_newest_first(client):
    client.post(
        "/api/quizzes",
        json={"title": "First Quiz", "lesson_text": SAMPLE_LESSON, "age": 9},
    )
    client.post(
        "/api/quizzes",
        json={"title": "Second Quiz", "lesson_text": SAMPLE_LESSON, "age": 11},
    )

    response = client.get("/api/quizzes?page=1&size=10")
    assert response.status_code == 200
    quizzes = response.json()
    assert len(quizzes) >= 2
    assert quizzes[0]["title"] == "Second Quiz"
