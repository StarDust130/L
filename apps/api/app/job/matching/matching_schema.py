from pydantic import BaseModel, Field


class AICompatibilityResult(BaseModel):
    """🤖 Validated AI compatibility result."""

    score: float = Field(
        ge=0,
        le=100,
    )
