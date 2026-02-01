import logging
import time
from collections.abc import AsyncIterator
from typing import Any, TypeVar, cast

import google.generativeai as genai
from aiolimiter import AsyncLimiter
from google.generativeai.types import (
    GenerationConfig,
)
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T", bound=BaseModel)

# Configure logging
logger = logging.getLogger(__name__)

# Model configurations for specific tasks
MODEL_CONFIGS = {
    "resume_enhancement": {
        "model": "gemini-1.5-pro",  # Note: gemini-1.5 is the current stable
        "temperature": 0.3,
        "max_output_tokens": 2000,
    },
    "cover_letter": {
        "model": "gemini-1.5-pro",
        "temperature": 0.7,
        "max_output_tokens": 1500,
    },
    "question_answering": {
        "model": "gemini-1.5-flash",
        "temperature": 0.4,
        "max_output_tokens": 500,
    },
}


class GeminiClient:
    """
    Robust wrapper for Google Gemini API with retries, rate limiting,
    token counting, and structured output support.
    """

    def __init__(
        self,
        api_key: str,
        default_model: str = "gemini-1.5-flash",
        requests_per_minute: int = 60,
    ):
        genai.configure(api_key=api_key)  # type: ignore[attr-defined]
        self.default_model_name = default_model
        self.limiter = AsyncLimiter(requests_per_minute, 60)

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.start_time = time.time()

    def _get_model(self, model_name: str | None = None) -> Any:
        # Returning Any because genai.GenerativeModel is not
        # explicitly exported for mypy
        return genai.GenerativeModel(  # type: ignore[attr-defined]
            model_name or self.default_model_name
        )

    def _update_token_counts(self, response: Any) -> None:
        try:
            usage = response.usage_metadata
            self.total_input_tokens += usage.prompt_token_count
            self.total_output_tokens += usage.candidates_token_count
            logger.info(
                f"Tokens used - Input: {usage.prompt_token_count}, "
                f"Output: {usage.candidates_token_count}"
            )
        except AttributeError:
            logger.warning("Could not extract usage metadata from response")

    @retry(
        retry=retry_if_exception_type(Exception),  # More specific errors in production
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
    )
    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        """Standard text generation with retries and rate limiting."""
        async with self.limiter:
            model_name = kwargs.pop("model", self.default_model_name)
            model = self._get_model(model_name)

            config = GenerationConfig(**kwargs)
            response = await model.generate_content_async(
                prompt, generation_config=config, request_options={"timeout": 30}
            )

            self._update_token_counts(response)
            return cast(str, response.text)

    async def generate_structured(
        self, prompt: str, schema: type[T], **kwargs: Any
    ) -> T:
        """Generate structured data using Pydantic models."""
        async with self.limiter:
            model_name = kwargs.pop("model", "gemini-1.5-pro")  # Better for structured
            model = self._get_model(model_name)

            # Gemini supports response_mime_type="application/json"
            # and response_schema for constrained output
            config = GenerationConfig(
                response_mime_type="application/json", response_schema=schema, **kwargs
            )

            response = await model.generate_content_async(
                prompt, generation_config=config, request_options={"timeout": 60}
            )
            self._update_token_counts(response)

            return schema.model_validate_json(response.text)

    async def generate_with_context(
        self,
        system: str,
        user: str,
        history: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> str:
        """Chat-style generation with system instructions and history."""
        async with self.limiter:
            model_name = kwargs.pop("model", self.default_model_name)
            # system_instruction is supported in newer versions
            model = genai.GenerativeModel(  # type: ignore[attr-defined]
                model_name=model_name, system_instruction=system
            )

            chat = model.start_chat(history=history or [])  # type: ignore[arg-type]
            response = await chat.send_message_async(
                user,
                generation_config=GenerationConfig(**kwargs),
                request_options={"timeout": 30},
            )

            self._update_token_counts(response)
            return cast(str, response.text)

    async def count_tokens(self, text: str, model_name: str | None = None) -> int:
        """Count tokens for a given text."""
        model = self._get_model(model_name)
        response = await model.count_tokens_async(text)
        return cast(int, response.total_tokens)

    async def embed_text(
        self, text: str, task_type: str = "RETRIEVAL_DOCUMENT"
    ) -> list[float]:
        """Generate vector embeddings for text."""
        async with self.limiter:
            # Note: embeddings use a different model family
            result = await genai.embed_content_async(  # type: ignore[attr-defined]
                model="models/text-embedding-004", content=text, task_type=task_type
            )
            return result["embedding"]

    async def stream_text(self, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Streaming text generation."""
        async with self.limiter:
            model_name = kwargs.pop("model", self.default_model_name)
            model = self._get_model(model_name)

            config = GenerationConfig(**kwargs)
            response = await model.generate_content_async(
                prompt, generation_config=config, stream=True
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

    def get_usage_metrics(self) -> dict[str, Any]:
        """Get summary of token usage and uptime."""
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "uptime_seconds": time.time() - self.start_time,
        }
