from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.core.ai.gemini_client import GeminiClient


class MockSchema(BaseModel):
    name: str
    score: int


@pytest.fixture
def gemini_client():
    return GeminiClient(api_key="test_key")


@pytest.mark.asyncio
async def test_generate_text_success(gemini_client):
    mock_response = MagicMock()
    mock_response.text = "Hello world"
    mock_response.usage_metadata.prompt_token_count = 5
    mock_response.usage_metadata.candidates_token_count = 2

    with patch(
        "google.generativeai.GenerativeModel.generate_content_async",
        new_callable=AsyncMock,
    ):
        google_gen_mock = "google.generativeai.GenerativeModel.generate_content_async"
        with patch(google_gen_mock, new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await gemini_client.generate_text("Say hello")

            assert result == "Hello world"
            assert gemini_client.total_input_tokens == 5
            assert gemini_client.total_output_tokens == 2


@pytest.mark.asyncio
async def test_generate_structured_success(gemini_client):
    mock_response = MagicMock()
    mock_response.text = '{"name": "Test", "score": 95}'
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5

    google_gen_mock = "google.generativeai.GenerativeModel.generate_content_async"
    with patch(google_gen_mock, new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = mock_response

        result = await gemini_client.generate_structured("Get stats", MockSchema)

        assert isinstance(result, MockSchema)
        assert result.name == "Test"
        assert result.score == 95


@pytest.mark.asyncio
async def test_count_tokens(gemini_client):
    mock_response = MagicMock()
    mock_response.total_tokens = 42

    with patch(
        "google.generativeai.GenerativeModel.count_tokens_async",
        new_callable=AsyncMock,
    ) as mock_count:
        mock_count.return_value = mock_response

        tokens = await gemini_client.count_tokens("How many tokens?")

        assert tokens == 42


@pytest.mark.asyncio
async def test_embed_text(gemini_client):
    mock_result = {"embedding": [0.1, 0.2, 0.3]}

    with patch(
        "google.generativeai.embed_content_async", new_callable=AsyncMock
    ) as mock_embed:
        mock_embed.return_value = mock_result

        embedding = await gemini_client.embed_text("Vectorize me")

        assert embedding == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_generate_with_context(gemini_client):
    mock_response = MagicMock()
    mock_response.text = "Response with context"
    mock_response.usage_metadata.prompt_token_count = 20
    mock_response.usage_metadata.candidates_token_count = 10

    mock_chat = MagicMock()
    mock_chat.send_message_async = AsyncMock(return_value=mock_response)

    with patch(
        "google.generativeai.GenerativeModel.start_chat", return_value=mock_chat
    ):
        result = await gemini_client.generate_with_context(
            system="System instr", user="User query"
        )

        assert result == "Response with context"


@pytest.mark.asyncio
async def test_stream_text(gemini_client):
    async def mock_generator():
        yield MagicMock(text="Part 1")
        yield MagicMock(text="Part 2")

    google_gen_mock = "google.generativeai.GenerativeModel.generate_content_async"
    with patch(google_gen_mock, return_value=mock_generator()):
        chunks = []
        async for chunk in gemini_client.stream_text("Stream this"):
            chunks.append(chunk)

        assert chunks == ["Part 1", "Part 2"]
