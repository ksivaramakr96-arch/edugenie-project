from __future__ import annotations

from functools import lru_cache

from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas import (
    LearningPathResponse,
    QuizResponse,
)


class GeminiServiceError(RuntimeError):
    """Raised when Gemini cannot complete an operation."""


@lru_cache
def get_client() -> genai.Client:
    settings = get_settings()

    if not settings.gemini_api_key:
        raise GeminiServiceError(
            "GEMINI_API_KEY is not configured. "
            "Add it to the .env file and restart the server."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _generate(
    prompt: str,
    *,
    schema=None,
) -> str:

    settings = get_settings()

    try:
        config = types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=1800,
            system_instruction=(
                "You are EduGenie, a patient and helpful educational assistant. "
                "Give accurate educational information. "
                "Use simple language when appropriate. "
                "Do not invent facts. "
                "If information is uncertain, clearly say so."
            ),
        )

        if schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = schema

        response = get_client().models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=config,
        )

        text = (response.text or "").strip()

        if not text:
            raise GeminiServiceError(
                "Gemini returned an empty response."
            )

        return text

    except GeminiServiceError:
        raise

    except Exception as exc:
        raise GeminiServiceError(
            f"Gemini request failed: {exc}"
        ) from exc


# ---------------------------------------------------------
# Q&A
# ---------------------------------------------------------

def answer_question(text: str) -> str:

    prompt = f"""
Answer the learner's question accurately and concisely.

Rules:
- Explain the answer clearly.
- Use simple language.
- If useful, provide a small example.
- If the question is ambiguous, mention the interpretation you used.
- Do not invent information.

Learner question:

{text}
"""

    return _generate(prompt)


# ---------------------------------------------------------
# Summarization
# ---------------------------------------------------------

def summarize(text: str) -> str:

    prompt = f"""
Summarize the following educational material.

Requirements:
- Preserve important facts.
- Preserve important concepts.
- Preserve important numbers or relationships.
- Use simple language.
- Prefer short paragraphs and bullet points.
- Do not add information that is not supported by the source text.

Educational material:

{text}
"""

    return _generate(prompt)


# ---------------------------------------------------------
# Quiz
# ---------------------------------------------------------

def generate_quiz(text: str) -> QuizResponse:

    prompt = f"""
Create exactly THREE multiple-choice questions based on
the supplied topic or study material.

Requirements:

1. Exactly 3 questions.
2. Exactly 4 options for every question.
3. Exactly one correct answer.
4. correct_answer must exactly match one of the options.
5. Include a short explanation.
6. Avoid trick questions.
7. Questions should test understanding rather than random details.

Study material:

{text}
"""

    raw = _generate(
        prompt,
        schema=QuizResponse,
    )

    try:
        return QuizResponse.model_validate_json(raw)

    except Exception as exc:
        raise GeminiServiceError(
            f"Gemini returned invalid quiz JSON: {exc}"
        ) from exc


# ---------------------------------------------------------
# Learning recommendations
# ---------------------------------------------------------

def learning_recommendations(
    text: str,
) -> LearningPathResponse:

    prompt = f"""
Create a structured learning path for the learner.

Start from beginner level and gradually move toward
advanced understanding.

Requirements:

- Identify the topic.
- Define a useful learning goal.
- Create 4 to 6 progressive learning steps.
- Each step must contain:
  - level
  - topic
  - concepts
  - suggested_time
  - resources
- Include practical study tips.
- Do not fabricate URLs.
- Resource entries can be resource types or search phrases.

Learner request:

{text}
"""

    raw = _generate(
        prompt,
        schema=LearningPathResponse,
    )

    try:
        return LearningPathResponse.model_validate_json(raw)

    except Exception as exc:
        raise GeminiServiceError(
            f"Gemini returned invalid learning-path JSON: {exc}"
        ) from exc