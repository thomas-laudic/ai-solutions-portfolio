"""HTTP boundaries for the TrustReply API and local demo."""

from typing import Annotated

from fastapi import FastAPI
from fastapi.params import Query
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse

from trustreply.models import QuestionResult
from trustreply.service import answer_question
from trustreply.web import render_demo_page


app = FastAPI(title="TrustReply", version="0.1.0")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.get("/", response_class=HTMLResponse)
def demo_page(
    question: Annotated[str | None, Query(min_length=1, max_length=500)] = None,
) -> HTMLResponse:
    result = answer_question(question) if question is not None else None
    return HTMLResponse(render_demo_page(question, result))


@app.post("/questions")
def evaluate_question(request: QuestionRequest) -> QuestionResult:
    return answer_question(request.question)
