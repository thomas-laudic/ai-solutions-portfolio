"""Small server-rendered demo page for the TrustReply decision result."""

from html import escape

from trustreply.models import Evidence, QuestionResult


EXAMPLE_QUESTIONS = (
    "Is customer data encrypted at rest?",
    "Is all customer data stored exclusively in the European Union?",
    "Do you provide customer-managed encryption keys?",
)

ROUTE_LABELS = {
    "auto_draft": "Auto draft",
    "human_review": "Human review",
    "insufficient_evidence": "Insufficient evidence",
}

STATUS_LABELS = {
    "draft_ready_for_human_check": "Draft ready for human check",
    "review_required": "Review required",
    "safe_abstention": "Safe abstention",
}


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _render_evidence(evidence: Evidence) -> str:
    return f"""
      <article class="evidence-card">
        <h4>{escape(evidence.title)}</h4>
        <blockquote>{escape(evidence.excerpt)}</blockquote>
        <p class="metadata">
          Approved: {_yes_no(evidence.approved)} ·
          Current: {_yes_no(evidence.current)} ·
          Shareable: {_yes_no(evidence.shareable)}
        </p>
      </article>"""


def _render_result(question: str, result: QuestionResult) -> str:
    draft = ""
    if result.draft is not None:
        draft = f"""
      <section id="draft" class="panel">
        <h3>Draft</h3>
        <p>{escape(result.draft)}</p>
      </section>"""

    review = ""
    if result.review_owner is not None:
        review = f'<p class="review-owner">Review owner: {escape(result.review_owner)}</p>'

    abstention = ""
    if result.route == "insufficient_evidence":
        abstention = f"""
      <section id="abstention" class="panel warning">
        <h3>Safe abstention</h3>
        <p>{escape(result.justification)}</p>
      </section>"""

    evidence = ""
    if result.evidence:
        cards = "".join(_render_evidence(item) for item in result.evidence)
        evidence = f'<section id="evidence" class="panel"><h3>Evidence</h3>{cards}</section>'

    return f"""
    <section id="result" data-route="{result.route}">
      <div class="result-heading">
        <div>
          <p class="eyebrow">Decision</p>
          <h2>{ROUTE_LABELS[result.route]}</h2>
        </div>
        <span class="status">{STATUS_LABELS.get(result.status, escape(result.status))}</span>
      </div>
      <p class="submitted-question">{escape(question)}</p>
      <p>{escape(result.justification)}</p>
      {review}
      {draft}
      {abstention}
      {evidence}
      <p class="metrics">Cost: ${result.cost_usd:.4f} · Latency: {result.latency_ms:.3f} ms</p>
    </section>"""


def render_demo_page(question: str | None, result: QuestionResult | None, trace_id: str | None = None) -> str:
    """Render the local demo without scripts or external assets."""
    examples = "".join(
        f'<form method="post" action="/"><button name="question" value="{escape(example, quote=True)}">{escape(example)}</button></form>'
        for example in EXAMPLE_QUESTIONS
    )
    result_html = _render_result(question, result) if question is not None and result is not None else ""
    if trace_id is not None:
        result_html += f'<p class="metrics">Trace: {escape(trace_id)}</p>'
    question_value = escape(question or "", quote=True)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>TrustReply demo</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    body {{ margin: 0; background: #f3f6f4; color: #18231d; }}
    main {{ width: min(880px, calc(100% - 32px)); margin: 48px auto; }}
    header, form, #result {{ background: #fff; border: 1px solid #d8e1dc; border-radius: 16px; padding: 24px; }}
    header {{ margin-bottom: 18px; }}
    h1, h2, h3, h4, p {{ margin-top: 0; }}
    h1 {{ margin-bottom: 8px; }}
    .scope {{ color: #536159; margin-bottom: 0; }}
    label, .eyebrow {{ display: block; font-weight: 700; margin-bottom: 8px; }}
    input {{ box-sizing: border-box; width: 100%; border: 1px solid #9aaba1; border-radius: 10px; padding: 12px; font: inherit; }}
    button {{ margin-top: 12px; border: 0; border-radius: 10px; padding: 11px 18px; background: #125c3b; color: white; font-weight: 700; cursor: pointer; }}
    .examples {{ display: grid; gap: 8px; margin: 16px 0 0; }}
    .examples a {{ color: #125c3b; }}
    #result {{ margin-top: 18px; }}
    .result-heading {{ display: flex; align-items: start; justify-content: space-between; gap: 16px; }}
    .eyebrow {{ color: #68776f; font-size: 0.75rem; letter-spacing: .08em; text-transform: uppercase; }}
    .status {{ background: #e7f2eb; border-radius: 999px; padding: 7px 11px; font-size: .85rem; }}
    .submitted-question {{ font-size: 1.1rem; font-weight: 650; }}
    .review-owner {{ border-left: 4px solid #af6c00; padding-left: 12px; font-weight: 700; }}
    .panel {{ margin-top: 18px; border-top: 1px solid #d8e1dc; padding-top: 18px; }}
    .warning {{ color: #734400; }}
    .evidence-card {{ background: #f7faf8; border-radius: 10px; padding: 16px; }}
    blockquote {{ margin: 0 0 12px; border-left: 3px solid #8ba697; padding-left: 12px; }}
    .metadata, .metrics {{ color: #5c6a62; font-size: .88rem; }}
    .metrics {{ margin: 20px 0 0; }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Controlled assistance</p>
      <h1>TrustReply</h1>
      <p class="scope">Synthetic corpus. A human must review any draft before sending.</p>
    </header>
    <form method="post" action="/">
      <label for="question">Question</label>
      <input id="question" name="question" value="{question_value}" minlength="1" maxlength="500" required>
      <button type="submit">Evaluate evidence</button>
    </form>
    <nav class="examples" aria-label="Example questions">{examples}</nav>
    {result_html}
  </main>
</body>
</html>"""
