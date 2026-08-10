from pydantic import BaseModel, Field


class AICompatibilityResult(BaseModel):
    """Validated result returned by the AI job matcher."""

    score: int = Field(
        ge=0,
        le=100,
    )
