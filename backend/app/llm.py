"""LLM integration for CI log analysis. Uses OpenRouter API with structured output."""

import os
import json
from openai import OpenAI

from .schemas import AnalyzeRequest, AnalyzeResponse, FailureClassification

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """You are a CI failure triage assistant. You analyze raw CI logs (from GitHub Actions or Jenkins) and extract structured information.

Your task is to:
1. Classify the failure as exactly one of: test_failure, lint_failure, infra_failure, config_failure, unknown.
2. Identify the step or job name where the failure likely occurred.
3. Pick the single most important error line from the log (the line that best explains the failure).
4. Write a clear, detailed explanation of why the failure happened.
5. Suggest a concrete next action for the developer.

Be concise but precise. Use the log content as the source of truth. If the log is empty or you cannot determine the failure, use classification "unknown" and explain that in the explanation."""


def _build_user_message(req: AnalyzeRequest) -> str:
    parts = ["Analyze this CI log and return a JSON object with: classification, failing_step, key_error_line, explanation, suggested_action.\n\n"]
    if req.ci_provider:
        parts.append(f"CI provider: {req.ci_provider.value}\n")
    if req.step_name:
        parts.append(f"Step name: {req.step_name}\n")
    if req.exit_code is not None:
        parts.append(f"Exit code: {req.exit_code}\n")
    parts.append("\n--- Log ---\n")
    parts.append(req.log_content or "(empty log)")
    parts.append("\n--- End log ---")
    return "".join(parts)


def analyze_log(req: AnalyzeRequest) -> AnalyzeResponse:
    """Send the log to the LLM and return structured analysis."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    client = OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)
    user_message = _build_user_message(req)

    response = client.chat.completions.create(
        model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    content = response.choices[0].message.content
    data = json.loads(content)

    # Normalize classification to enum
    raw_class = (data.get("classification") or "unknown").strip().lower()
    if raw_class in ("test_failure", "test failure"):
        classification = FailureClassification.TEST_FAILURE
    elif raw_class in ("lint_failure", "lint failure"):
        classification = FailureClassification.LINT_FAILURE
    elif raw_class in ("infra_failure", "infra failure", "infrastructure failure"):
        classification = FailureClassification.INFRA_FAILURE
    elif raw_class in ("config_failure", "config failure", "configuration failure"):
        classification = FailureClassification.CONFIG_FAILURE
    else:
        classification = FailureClassification.UNKNOWN

    return AnalyzeResponse(
        classification=classification,
        failing_step=(data.get("failing_step") or "Unknown").strip() or "Unknown",
        key_error_line=(data.get("key_error_line") or "").strip(),
        explanation=(data.get("explanation") or "").strip() or "No explanation could be extracted.",
        suggested_action=(data.get("suggested_action") or "").strip() or "Review the full log and retry.",
    )
