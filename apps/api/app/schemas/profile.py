from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CandidateProfile(BaseModel):
    # 🛡️ Reject unexpected fields
    model_config = ConfigDict(extra="forbid")

    full_name: str | None
    target_roles: list[str]
    skills: list[str]
    experience: list[str]
    education: list[str]
    locations: list[str]

    remote_preference: Literal[
        "remote",
        "hybrid",
        "onsite",
        "flexible",
        "unknown",
    ]

    years_of_experience: float | None
    work_authorization: str | None
    links: list[str]


class ProfileExtractionRequest(BaseModel):
    # ✂️ Limit text to control cost and processing time
    resume_text: str = Field(
        min_length=1,
        max_length=50_000,
    )
