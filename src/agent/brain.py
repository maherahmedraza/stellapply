import json
import logging
from typing import Any, Dict, List

import google.generativeai as genai
from pydantic import BaseModel, Field

from src.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class AgentAction(BaseModel):
    """
    Structured output representing the next action the agent should take.
    """

    action_type: str = Field(
        ...,
        description="Type of action: 'click', 'type', 'navigate', 'scroll', 'wait', 'finish', 'fail'",
    )
    selector: str | None = Field(
        None, description="CSS or XPath selector for the element to interact with"
    )
    value: str | None = Field(
        None, description="Value to type/fill or URL to navigate to"
    )
    description: str = Field(
        ..., description="Thinking process/reasoning for this action"
    )


class PageContext(BaseModel):
    """
    Context provided to the Brain about the current page state.
    """

    url: str
    title: str
    dom_snippet: str  # Simplified DOM or accessibility tree
    screenshot_b64: str | None = None


class AgentBrain:
    """
    The decision engine powered by Google Gemini.
    """

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(
            model_name, generation_config={"response_mime_type": "application/json"}
        )

    async def decide_next_action(
        self,
        task_description: str,
        page_context: PageContext,
        previous_actions: List[Dict[str, Any]],
    ) -> AgentAction:
        """
        Ask the LLM what to do next based on the current page and task.
        """

        prompt = f"""
        You are an autonomous browser agent. Your goal is: {task_description}

        Current Page:
        - URL: {page_context.url}
        - Title: {page_context.title}

        Page Content (Simplified):
        ```html
        {page_context.dom_snippet}
        ```

        History:
        {json.dumps(previous_actions, indent=2)}

        Decide the next action. Return JSON matching the AgentAction schema.
        Valid action_types: 'click', 'type', 'navigate', 'scroll', 'wait', 'finish', 'fail'.
        """

        try:
            # If screenshot is present, we can use multimodal input (future enhancement)
            # For now, text-based
            response = await self.model.generate_content_async(prompt)
            data = json.loads(response.text)
            return AgentAction(**data)
        except Exception as e:
            logger.error(f"Brain freeze: {e}")
            return AgentAction(
                action_type="fail", description=f"Error in decision process: {str(e)}"
            )

    async def extract_data(self, content: str, schema: dict) -> dict:
        """
        Extract specific structured data from raw content (e.g., job details).
        """
        prompt = f"""
        Extract data from the following text based on the schema:
        
        Text:
        {content[:10000]}... (truncated)

        Schema:
        {json.dumps(schema, indent=2)}
        """

        response = await self.model.generate_content_async(prompt)
        return json.loads(response.text)
