from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.schemas import (
    AnswerResponse,
    LearningPathResponse,
    QuizResponse,
    TextRequest,
)
from app.services import explanation as explanation_service
from app.services import gemini as gemini_service
from app.services.gemini import GeminiServiceError


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

settings = get_settings()


# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "EduGenie - AI-powered educational learning assistant "
        "using Google Gemini."
    ),
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Static files
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# ---------------------------------------------------------
# Error wrapper
# ---------------------------------------------------------

def _run(operation):

    try:
        return operation()

    except GeminiServiceError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {exc}",
        ) from exc


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get(
    "/",
    include_in_schema=False,
)
def index() -> FileResponse:

    return FileResponse(
        STATIC_DIR / "index.html"
    )


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:

    return {
        "status": "ok",
        "service": settings.app_name,
    }


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

@app.post(
    "/qa",
    response_model=AnswerResponse,
)
def qa(
    request: TextRequest,
) -> AnswerResponse:

    result = _run(
        lambda: gemini_service.answer_question(request.text)
    )

    return AnswerResponse(
        answer=result
    )


# ---------------------------------------------------------
# Explain
# ---------------------------------------------------------

@app.post(
    "/explain",
    response_model=AnswerResponse,
)
def explanation(
    request: TextRequest,
) -> AnswerResponse:

    result = _run(
        lambda: explanation_service.explain(request.text)
    )

    return AnswerResponse(
        answer=result
    )


# ---------------------------------------------------------
# Summarize
# ---------------------------------------------------------

@app.post(
    "/summarize",
    response_model=AnswerResponse,
)
def summary(
    request: TextRequest,
) -> AnswerResponse:

    result = _run(
        lambda: gemini_service.summarize(request.text)
    )

    return AnswerResponse(
        answer=result
    )


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

@app.post(
    "/quiz",
    response_model=QuizResponse,
)
def quiz(
    request: TextRequest,
) -> QuizResponse:

    return _run(
        lambda: gemini_service.generate_quiz(request.text)
    )


# ---------------------------------------------------------
# Learning recommendations
# ---------------------------------------------------------

@app.post(
    "/learn/recommendations",
    response_model=LearningPathResponse,
)
def recommendations(
    request: TextRequest,
) -> LearningPathResponse:

    return _run(
        lambda: gemini_service.learning_recommendations(request.text)
    )