from __future__ import annotations

from functools import lru_cache

from app.config import get_settings
from app.services.gemini import answer_question


class LocalExplanationService:
    """
    Optional local LaMini-Flan-T5 explanation service.

    The model is loaded only when explicitly enabled.
    """

    def __init__(self) -> None:
        self._tokenizer = None
        self._model = None

    def _load(self) -> None:

        settings = get_settings()

        try:
            from transformers import (
                AutoModelForSeq2SeqLM,
                AutoTokenizer,
            )

        except ImportError as exc:
            raise RuntimeError(
                "transformers is not installed."
            ) from exc

        self._tokenizer = AutoTokenizer.from_pretrained(
            settings.local_explanation_model
        )

        self._model = AutoModelForSeq2SeqLM.from_pretrained(
            settings.local_explanation_model
        )

    def explain(self, text: str) -> str:

        if self._model is None:
            self._load()

        prompt = (
            "Explain this educational concept simply "
            "with a short example:\n"
            f"{text}"
        )

        inputs = self._tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        output = self._model.generate(
            **inputs,
            max_new_tokens=220,
            num_beams=4,
        )

        return self._tokenizer.decode(
            output[0],
            skip_special_tokens=True,
        ).strip()


@lru_cache
def get_local_service() -> LocalExplanationService:
    return LocalExplanationService()


def explain(text: str) -> str:

    settings = get_settings()

    # Try local model if enabled.
    if settings.use_local_explanation_model:

        try:
            result = get_local_service().explain(text)

            if result:
                return result

        except Exception:
            # Fall back to Gemini.
            pass

    # Gemini fallback.
    return answer_question(
        """
Explain the following concept as if teaching
a complete beginner.

Requirements:
- Use simple language.
- Break the explanation into steps.
- Explain difficult terminology.
- Give one intuitive example.
- Keep it educational and easy to understand.

Concept:

"""
        + text
    )