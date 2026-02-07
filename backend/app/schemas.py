"""Request and response schemas for the CI log analysis API."""

from enum import Enum
from pydantic import BaseModel, Field


class CIProvider(str, Enum):
    GITHUB_ACTIONS = "github_actions"
    JENKINS = "jenkins"


class FailureClassification(str, Enum):
    TEST_FAILURE = "test_failure"
    LINT_FAILURE = "lint_failure"
    INFRA_FAILURE = "infra_failure"
    CONFIG_FAILURE = "config_failure"
    UNKNOWN = "unknown"


class AnalyzeRequest(BaseModel):
    log_content: str = Field(..., description="Raw CI log output pasted by the user")
    ci_provider: CIProvider | None = Field(
        default=None,
        description="Optional: GitHub Actions or Jenkins",
    )
    step_name: str | None = Field(default=None, description="Optional: name of the failing step")
    exit_code: int | None = Field(default=None, description="Optional: exit code if known")


class AnalyzeResponse(BaseModel):
    classification: FailureClassification = Field(
        ...,
        description="Failure type: test_failure, lint_failure, infra_failure, config_failure, unknown",
    )
    failing_step: str = Field(
        ...,
        description="The step or job name where the failure likely occurred",
    )
    key_error_line: str = Field(
        ...,
        description="The most important single error line from the log",
    )
    explanation: str = Field(
        ...,
        description="Detailed explanation of why the failure happened",
    )
    suggested_action: str = Field(
        ...,
        description="Suggested next action for the developer",
    )
