from dataclasses import dataclass
from typing import Literal

from app.agent.tools.jobs import JobRecommendation


@dataclass
class AgentResult:
    type: Literal["text", "jobs"]
    content: str
    jobs: list[JobRecommendation] | None = None
