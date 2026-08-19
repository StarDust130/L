from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.agent.agent import (
    _extract_failed_generation,
    _is_ambiguous_message,
    _parse_malformed_function_call,
    _select_tools_for_message,
    run_agent,
)
from app.agent.tools.job_validation import filter_job_quality
from app.agent.types import AgentResult
from app.db.db import ensure_sqlite_compatibility
from app.profile.profile_schema import CandidateProfile
from app.telegram.telegram_service import handle_chat_message


@pytest.mark.asyncio
async def test_sqlite_compatibility_adds_missing_job_fingerprint_column(
    tmp_path,
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'compat.db'}"
    engine = create_async_engine(database_url)

    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                CREATE TABLE companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255),
                    website VARCHAR(255),
                    source VARCHAR(50),
                    is_hiring BOOLEAN
                )
                """
            )
        )
        await connection.execute(
            text(
                """
                CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_id VARCHAR(100),
                    title VARCHAR(255),
                    company_id INTEGER,
                    location VARCHAR(255),
                    description TEXT,
                    salary VARCHAR(255),
                    apply_url VARCHAR(1000),
                    source VARCHAR(50),
                    FOREIGN KEY(company_id) REFERENCES companies(id)
                )
                """
            )
        )

    await ensure_sqlite_compatibility(engine)

    async with engine.begin() as connection:
        result = await connection.execute(text("PRAGMA table_info(jobs)"))
        names = [row[1] for row in result.fetchall()]

    assert "fingerprint" in names


@pytest.mark.asyncio
async def test_handle_chat_message_accepts_plain_string_agent_response() -> None:
    with (
        patch("app.telegram.telegram_service.send_typing", AsyncMock()),
        patch(
            "app.telegram.telegram_service.send_message",
            AsyncMock(),
        ) as mock_send_message,
        patch(
            "app.telegram.telegram_service.run_agent",
            AsyncMock(return_value="hello from agent"),
        ),
        patch(
            "app.telegram.telegram_service.select",
        ),
    ):

        class FakeSession:
            def add(self, *_args, **_kwargs):
                return None

            async def commit(self):
                return None

            async def execute(self, *_args, **_kwargs):
                class Result:
                    def scalar_one_or_none(self):
                        return SimpleNamespace(
                            clerk_user_id="user_123",
                            telegram_chat_id="chat_123",
                            profile={"preferences": []},
                        )

                return Result()

        await handle_chat_message(
            db=FakeSession(),
            chat_id="chat_123",
            message="remote only",
        )

    assert mock_send_message.await_count == 1
    payload = mock_send_message.await_args.kwargs
    assert payload["chat_id"] == "chat_123"
    assert payload["text"] == "hello from agent"


@pytest.mark.asyncio
async def test_handle_chat_message_handles_agent_exception_gracefully() -> None:
    with (
        patch("app.telegram.telegram_service.send_typing", AsyncMock()),
        patch(
            "app.telegram.telegram_service.send_message",
            AsyncMock(),
        ) as mock_send_message,
        patch(
            "app.telegram.telegram_service.run_agent",
            AsyncMock(side_effect=RuntimeError("agent failed")),
        ),
        patch(
            "app.telegram.telegram_service.select",
        ),
    ):

        class FakeSession:
            def add(self, *_args, **_kwargs):
                return None

            async def commit(self):
                return None

            async def execute(self, *_args, **_kwargs):
                class Result:
                    def scalar_one_or_none(self):
                        return SimpleNamespace(
                            clerk_user_id="user_123",
                            telegram_chat_id="chat_123",
                            profile={"preferences": []},
                        )

                return Result()

        await handle_chat_message(
            db=FakeSession(),
            chat_id="chat_123",
            message="find jobs",
        )

    assert mock_send_message.await_count == 1
    payload = mock_send_message.await_args.kwargs
    assert payload["chat_id"] == "chat_123"
    assert "temporary issue" in payload["text"]


def test_is_ambiguous_message_detects_low_signal_inputs() -> None:
    assert _is_ambiguous_message("hi") is True
    assert _is_ambiguous_message("ok") is True
    assert _is_ambiguous_message("find remote ai jobs") is False


def test_select_tools_for_message_gates_discovery_tools() -> None:
    recommendation_only = _select_tools_for_message("show my best matches")
    recommendation_names = {
        schema["function"]["name"] for schema in recommendation_only
    }
    assert recommendation_names == {"get_my_recommendations"}

    discovery_tools = _select_tools_for_message("discover new job boards for ai roles")
    discovery_names = {schema["function"]["name"] for schema in discovery_tools}
    assert "get_my_recommendations" in discovery_names
    assert "search_web" in discovery_names
    assert "fetch_page" in discovery_names
    assert "get_known_sources" in discovery_names
    assert "save_source" in discovery_names


def test_parse_malformed_function_call_with_attribute_arguments() -> None:
    failed_generation = '<function=search_web query="technology job boards"></function>'

    parsed = _parse_malformed_function_call(failed_generation)

    assert parsed is not None
    tool_name, arguments = parsed
    assert tool_name == "search_web"
    assert arguments == {"query": "technology job boards"}


def test_parse_malformed_function_call_with_body_arguments() -> None:
    failed_generation = (
        '<function=search_web>query="daily job automation tools"</function>'
    )

    parsed = _parse_malformed_function_call(failed_generation)

    assert parsed is not None
    tool_name, arguments = parsed
    assert tool_name == "search_web"
    assert arguments == {"query": "daily job automation tools"}


def test_extract_failed_generation_from_error_body() -> None:
    class FakeError(Exception):
        def __init__(self):
            self.body = {
                "error": {
                    "failed_generation": '<function=search_web query="x"></function>',
                }
            }

    failed_generation = _extract_failed_generation(FakeError())

    assert failed_generation == '<function=search_web query="x"></function>'


@pytest.mark.asyncio
async def test_run_agent_handles_llm_completion_exception() -> None:
    with patch(
        "app.agent.agent.client.chat.completions.create",
        AsyncMock(side_effect=RuntimeError("llm down")),
    ):
        result = await run_agent(
            db=SimpleNamespace(),
            message="find me jobs",
            user_id="user_123",
        )

    assert isinstance(result, AgentResult)
    assert result.type == "text"
    assert "temporary AI error" in result.content


@pytest.mark.asyncio
async def test_run_agent_recovers_from_malformed_function_tag_error() -> None:
    class FakeToolUseError(Exception):
        def __init__(self):
            self.body = {
                "error": {
                    "failed_generation": (
                        '<function=search_web query="technology job boards"></function>'
                    ),
                }
            }

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(
                    tool_calls=None,
                    content="Recovered answer",
                )
            )
        ]
    )

    with (
        patch(
            "app.agent.agent.client.chat.completions.create",
            AsyncMock(side_effect=[FakeToolUseError(), fake_response]),
        ),
        patch(
            "app.agent.agent._execute_tool",
            AsyncMock(return_value="[]"),
        ),
    ):
        result = await run_agent(
            db=SimpleNamespace(),
            message="discover technology job boards",
            user_id="user_123",
        )

    assert isinstance(result, AgentResult)
    assert result.type == "text"
    assert result.content == "Recovered answer"


@pytest.mark.asyncio
async def test_run_agent_rejects_off_scope_malformed_tool_recovery() -> None:
    class FakeToolUseError(Exception):
        def __init__(self):
            self.body = {
                "error": {
                    "failed_generation": (
                        '<function=search_web query="technology job boards"></function>'
                    ),
                }
            }

    with patch(
        "app.agent.agent.client.chat.completions.create",
        AsyncMock(side_effect=FakeToolUseError()),
    ):
        result = await run_agent(
            db=SimpleNamespace(),
            message="show my recommendations",
            user_id="user_123",
        )

    assert isinstance(result, AgentResult)
    assert result.type == "text"
    assert "need a bit more detail" in result.content


@pytest.mark.asyncio
async def test_run_agent_returns_clarification_for_ambiguous_message() -> None:
    with patch(
        "app.agent.agent.client.chat.completions.create",
        AsyncMock(),
    ) as completion_mock:
        result = await run_agent(
            db=SimpleNamespace(),
            message="hi",
            user_id="user_123",
        )

    assert isinstance(result, AgentResult)
    assert result.type == "text"
    assert "need one detail first" in result.content
    completion_mock.assert_not_awaited()


def test_filter_job_quality_is_not_globally_technical_only() -> None:
    job = {
        "title": "Product Manager",
        "company": "Acme AI",
        "description": "Lead AI product roadmap and GTM strategy.",
        "apply_url": None,
        "location": "Remote",
        "salary": None,
    }

    result = filter_job_quality(job)

    assert result.passed is True


def test_profile_schema_accepts_preferences() -> None:
    profile = CandidateProfile.model_validate(
        {
            "full_name": "Aman Sharma",
            "target_roles": ["Frontend Engineer"],
            "skills": ["TypeScript", "React"],
            "experience": ["Built web apps"],
            "education": ["B.Tech"],
            "locations": ["Remote"],
            "remote_preference": "remote",
            "years_of_experience": 2,
            "work_authorization": "India",
            "links": ["https://github.com/example"],
            "preferences": ["remote only", "AI startups", "frontend internships"],
        }
    )

    assert profile.preferences == [
        "remote only",
        "AI startups",
        "frontend internships",
    ]
