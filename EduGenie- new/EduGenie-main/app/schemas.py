from pydantic import BaseModel, Field, field_validator


class TextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Question, topic, or study material",
    )

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Input cannot be empty")

        return value


class AnswerResponse(BaseModel):
    answer: str


class QuizQuestion(BaseModel):
    question: str

    options: list[str] = Field(
        ...,
        min_length=4,
        max_length=4,
    )

    correct_answer: str

    explanation: str = ""


class QuizResponse(BaseModel):
    questions: list[QuizQuestion] = Field(
        ...,
        min_length=3,
        max_length=3,
    )


class LearningStep(BaseModel):
    level: str
    topic: str

    concepts: list[str]

    suggested_time: str

    resources: list[str]


class LearningPathResponse(BaseModel):
    topic: str
    goal: str

    steps: list[LearningStep]

    study_tips: list[str]