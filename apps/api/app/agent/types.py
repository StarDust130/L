from dataclasses import dataclass
from typing import Literal


@dataclass
class AgentResult:
    type: Literal["text", "jobs"]
    content: str | None = None
    jobs: list[dict[str, object]] | None = None
