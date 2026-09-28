from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.services import gemini
from app.services import explanation
from app.schemas import (
    LearningPathResponse,
    QuizResponse,
)


client = TestClient(app)


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

def test_settings_loads_project_dotenv_from_repo_root(monkeypatch):
    project_root = Path(__file__).resolve().parents[1]
    env_path = project_root / ".env"
    original = env_path.read_text(encoding="utf-8") if env_path.exists() else None

    try:
        env_path.write_text(
            "GEMINI_API_KEY=from_repo_dotenv\n"
            "GEMINI_MODEL=gemini-3.8-flash\n",
            encoding="utf-8",
        )

        monkeypatch.chdir(project_root.parent)
        settings = Settings()

        assert settings.gemini_api_key == "from_repo_dotenv"
        assert settings.gemini_model == "gemini-3.8-flash"
    finally:
        if original is None:
            env_path.unlink(missing_ok=True)
        else:
            env_path.write_text(original, encoding="utf-8")


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

def test_frontend_is_served():

    response = client.get("/")

    assert response.status_code == 200

    assert "EduGenie" in response.text


def test_frontend_html_is_clean():

    html = Path("static/index.html").read_text(encoding="utf-8")

    assert not html.startswith("@'")
    assert "<!doctype html>" in html.lower()


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

def test_qa(monkeypatch):

    monkeypatch.setattr(
        gemini,
        "answer_question",
        lambda text: "The answer is 42.",
    )

    response = client.post(
        "/qa",
        json={
            "text": "What is the answer?"
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "answer": "The answer is 42."
    }


# ---------------------------------------------------------
# Explanation
# ---------------------------------------------------------

def test_explain(monkeypatch):

    monkeypatch.setattr(
        explanation,
        "explain",
        lambda text: "Simple explanation.",
    )

    response = client.post(
        "/explain",
        json={
            "text": "Photosynthesis"
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["answer"]
        == "Simple explanation."
    )


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

def test_quiz(monkeypatch):

    quiz = QuizResponse.model_validate(
        {
            "questions": [
                {
                    "question": f"Q{i}",
                    "options": [
                        "A",
                        "B",
                        "C",
                        "D",
                    ],
                    "correct_answer": "A",
                    "explanation": "Because A.",
                }
                for i in range(3)
            ]
        }
    )

    monkeypatch.setattr(
        gemini,
        "generate_quiz",
        lambda text: quiz,
    )

    response = client.post(
        "/quiz",
        json={
            "text": "Pythagoras theorem"
        },
    )

    assert response.status_code == 200

    assert len(
        response.json()["questions"]
    ) == 3


# ---------------------------------------------------------
# Learning path
# ---------------------------------------------------------

def test_learning_path(monkeypatch):

    path = LearningPathResponse.model_validate(
        {
            "topic": "SQL",

            "goal": "Become job-ready",

            "steps": [
                {
                    "level": "Beginner",

                    "topic": "SELECT",

                    "concepts": [
                        "tables"
                    ],

                    "suggested_time": "2 days",

                    "resources": [
                        "official docs"
                    ],
                }
            ],

            "study_tips": [
                "Practice daily"
            ],
        }
    )

    monkeypatch.setattr(
        gemini,
        "learning_recommendations",
        lambda text: path,
    )

    response = client.post(
        "/learn/recommendations",
        json={
            "text": "Learn SQL"
        },
    )

    assert response.status_code == 200

    assert (
        response.json()["topic"]
        == "SQL"
    )


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------

def test_empty_input_is_rejected():

    response = client.post(
        "/qa",
        json={
            "text": "   "
        },
    )

    assert response.status_code == 422