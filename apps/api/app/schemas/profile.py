from typing import Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    full_name: str | None = None
    target_roles: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    remote_preference: Literal[
        "remote",
        "hybrid",
        "onsite",
        "unknown",
    ] = "unknown"
    years_of_experience: float | None = None
    work_authorization: str | None = None
    links: list[str] = Field(default_factory=list)
