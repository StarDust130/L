import json

from app.core.config import get_settings
from app.profile.profile_schema import CandidateProfile
from fastapi import HTTPException
from groq import Groq
from pydantic import ValidationError


def extract_candidate_profile(resume_text: str) -> CandidateProfile:
    settings = get_settings()

    # 🤖 Create the Groq client on the backend
    client = Groq(api_key=settings.groq_api_key)

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": """
You extract structured candidate information from resumes.

Rules:
- Use only facts clearly present in the resume.
- Never invent skills, companies, education, or experience.
- Use null when one value is unknown.
- Use an empty list when no values are found.
- Return only the requested JSON structure.
""",
                },
                {
                    "role": "user",
                    "content": resume_text,
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "candidate_profile",
                    "strict": True,
                    "schema": CandidateProfile.model_json_schema(),
                },
            },
        )

        # 📦 Read the structured AI response
        content = response.choices[0].message.content

        if not content:
            raise HTTPException(
                status_code=502,
                detail="Groq returned an empty response",
            )

        # ✅ Validate that the AI returned our expected shape
        return CandidateProfile.model_validate_json(content)

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=502,
            detail="Groq returned invalid JSON",
        ) from error

    except ValidationError as error:
        raise HTTPException(
            status_code=502,
            detail="Groq returned an invalid candidate profile",
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Profile extraction failed",
        ) from error


"""
AI output → Pydantic validation → trusted application data
"""
