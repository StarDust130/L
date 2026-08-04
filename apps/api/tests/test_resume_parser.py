from io import BytesIO

import pytest
from app.services.resume_parser import extract_resume_text
from fastapi import UploadFile


@pytest.mark.anyio
async def test_extract_txt_resume() -> None:
    file = UploadFile(
        file=BytesIO(
            b"Python Developer\nFastAPI\nPostgreSQL",
        ),
        filename="resume.txt",
    )

    result = await extract_resume_text(file)

    assert result.file_type == "txt"
    assert "FastAPI" in result.text
    assert result.character_count > 0
