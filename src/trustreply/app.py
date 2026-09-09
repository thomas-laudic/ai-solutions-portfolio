"""HTTP boundary for the first TrustReply vertical slice."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from trustreply.service import answer_question


app = FastAPI(title="TrustReply", version="0.1.0")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.post("/questions")
def evaluate_question(request: QuestionRequest) -> dict[str, object]:
    return answer_question(request.question)
