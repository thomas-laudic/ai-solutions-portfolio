"""HTTP boundaries for the TrustReply API and local demo."""

from typing import Annotated
from urllib.parse import parse_qs

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field, ValidationError
from starlette.concurrency import run_in_threadpool
from starlette.responses import HTMLResponse

from trustreply.models import QuestionResult
from trustreply.audit import AuditSink, evaluate_with_audit, get_audit_sink
from trustreply.web import render_demo_page


app = FastAPI(title="TrustReply", version="0.1.0")


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


@app.get("/", response_class=HTMLResponse)
def demo_page() -> HTMLResponse:
    return HTMLResponse(render_demo_page(None, None))


@app.post("/", response_class=HTMLResponse)
async def evaluate_demo(request: Request, sink: Annotated[AuditSink, Depends(get_audit_sink)]) -> HTMLResponse:
    # Standard-library parser avoids a multipart dependency for one text field.
    if request.headers.get("content-type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
        raise HTTPException(415, "Expected URL-encoded form")
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 8192:
            raise HTTPException(413, "Form too large")
    try:
        fields = parse_qs(body.decode("utf-8"), keep_blank_values=True, max_num_fields=2, errors="strict")
        if set(fields) != {"question"} or len(fields["question"]) != 1:
            raise ValueError("Expected one question")
        payload = QuestionRequest(question=fields["question"][0])
    except (ValueError, ValidationError):
        raise HTTPException(422, "Expected one question of 1 to 500 characters") from None
    result, event = await run_in_threadpool(evaluate_with_audit, payload.question, sink, channel="web")
    return HTMLResponse(
        render_demo_page(payload.question, result, str(event.trace_id)),
        headers={"X-Trace-ID": str(event.trace_id), "Cache-Control": "no-store"},
    )


@app.post("/questions")
def evaluate_question(
    request: QuestionRequest, response: Response, sink: Annotated[AuditSink, Depends(get_audit_sink)],
) -> QuestionResult:
    result, event = evaluate_with_audit(request.question, sink, channel="api")
    response.headers["X-Trace-ID"] = str(event.trace_id)
    response.headers["Cache-Control"] = "no-store"
    return result
