import base64
import json
import logging
from datetime import datetime
from typing import Any

# Updated import for google.generativeai
try:
    import google.generativeai as genai
except ImportError:
    # Fallback or stub for running without api key in some envs
    genai = None

from pydantic import ValidationError

from src.agent.models.schemas import AgentAction, PageContext
from src.core.config import settings
from src.modules.profile.schemas import UserProfileResponse

logger = logging.getLogger(__name__)

# Configure Gemini
if settings.ai.GEMINI_API_KEY:
    genai.configure(api_key=settings.ai.GEMINI_API_KEY)


class AgentBrain:
    """
    The unified, stateful decision engine powered by Google Gemini.
    """

    def __init__(
        self, profile: UserProfileResponse, model_name: str = "gemini-3.0-flash"
    ):
        """
        Brain is initialized ONCE per agent run with the user's profile.
        Profile stays in memory for the entire session.
        """
        self.profile = profile
        self.conversation_history: list[dict[str, Any]] = []
        self.action_count = 0
        self.page_action_count = 0
        self.current_url = ""

        # Initialize model
        # Using gemini-3.0-flash as default
        # Adjust based on availability
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name, generation_config={"response_mime_type": "application/json"}
        )

    def _build_system_prompt(self, goal: str) -> str:
        """
        Build a comprehensive system prompt with full profile injection.
        """
        p = self.profile
        pi = p.personal_info
        sp = p.search_preferences

        # Format Experience
        experience_text = ""
        for exp in p.experience:
            experience_text += (
                f"- {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date or 'Present'})\n"
                f"  Location: {exp.location}\n"
                f"  Description: {exp.description}\n"
            )

        # Format Education
        education_text = ""
        for edu in p.education:
            education_text += f"- {edu.degree} in {edu.field_of_study} from {edu.institution} ({edu.end_date})\n"

        # Format Answers
        answers_text = ""
        if p.application_answers:
            # Iterate over all fields that are not None
            for k, v in p.application_answers.model_dump(exclude_none=True).items():
                answers_text += f"Q: {k} -> A: {v}\n"

        # Format Rules
        rules_text = ""
        if p.agent_rules:
            for k, v in p.agent_rules.model_dump(exclude_none=True).items():
                rules_text += f"- {k}: {v}\n"

        # Salary formatting
        salary_info = "Not specified"
        if sp.salary_expectations:
            salary_info = f"{sp.salary_expectations.min} - {sp.salary_expectations.max} {sp.salary_expectations.currency}"

        prompt = f"""
        You are an AI agent that helps a user apply to jobs by navigating websites.
        
        ## YOUR USER'S COMPLETE PROFILE:
        
        ### Personal Information:
        - Full Name: {pi.first_name} {pi.last_name}
        - Email: {pi.email}
        - Phone: {pi.phone}
        - Location: {pi.address.city}, {pi.address.country if pi.address else ""}
        - LinkedIn: {pi.linkedin_url}
        - Portfolio: {pi.portfolio_url}
        
        ### Professional Experience:
        {experience_text}
        
        ### Education:
        {education_text}
        
        ### Skills:
        - Technical: {", ".join(p.skills)} (Check consistency with Experience)
        
        ### Pre-answered Application Questions:
        {answers_text}
        
        ### Agent Rules:
        {rules_text}
        
        ### Search Preferences:
        - Target Roles: {", ".join(sp.target_roles)}
        - Salary: {salary_info}
        
        ## YOUR CURRENT GOAL:
        {goal}
        
        ## RULES:
        1. Only define ONE action at a time.
        2. Respond with valid JSON matching AgentAction schema.
        3. Do NOT fabricate information. If a required field is missing from profile, request HUMAN_HANDOFF.
        4. Prefer 'click' on 'Apply' or 'Submit' buttons.
        5. If CAPTCHA is detected, request HUMAN_HANDOFF.
        6. Return TASK_COMPLETE if you see a success confirmation.
        """
        return prompt

    async def decide_next_action(
        self, goal: str, page_context: PageContext, error_context: str | None = None
    ) -> AgentAction:
        """
        Decide the next action based on goal, profile, history, and current page.
        """

        # Track page changes
        if page_context.url != self.current_url:
            self.current_url = page_context.url
            self.page_action_count = 0

        self.action_count += 1
        self.page_action_count += 1

        # Loop detection (simple)
        if self.page_action_count > 15:
            return AgentAction(
                thinking="I have been stuck on this page for too many steps.",
                action_type="human_handoff",
                confidence=0.0,
                expected_result="Human intervention",
            )

        system_instructions = self._build_system_prompt(goal)

        # Build Context Prompt
        history_snippet = json.dumps(self.conversation_history[-5:], indent=2)

        # Token Management: Truncate DOM if too large (naive)
        dom_snippet = page_context.dom_snippet
        if len(dom_snippet) > 20000:
            dom_snippet = dom_snippet[:20000] + "...(truncated)"

        user_prompt = f"""
        ## WHAT YOU SEE RIGHT NOW:
        URL: {page_context.url}
        Title: {page_context.title}
        
        ## PAGE DOM (Snippet):
        ```html
        {dom_snippet}
        ```
        
        ## FORMS DETECTED:
        {json.dumps(page_context.forms, indent=2)}
        
        ## HISTORY (Last 5 actions):
        {history_snippet}
        
        {f"## PREVIOUS ERROR: {error_context}" if error_context else ""}
        
        Decide the next action.
        """

        if page_context.screenshot_b64:
            user_prompt += "\n\nI have attached a screenshot of the page. Use it to verify layout and find buttons."

        # Prepare arguments
        parts = [system_instructions + "\n\n" + user_prompt]

        # Multimodal
        if page_context.screenshot_b64:
            try:
                image_bytes = base64.b64decode(page_context.screenshot_b64)
                parts.append({"mime_type": "image/jpeg", "data": image_bytes})
            except Exception as e:
                logger.error(f"Failed to decode screenshot: {e}")

        # Retry Logic
        for attempt in range(3):
            try:
                response = await self.model.generate_content_async(parts)
                text = response.text.strip()

                # Unwrap markdown
                if text.startswith("```"):
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    else:
                        text = text.split("```")[1].split("```")[0].strip()

                data = json.loads(text)
                action = AgentAction(**data)

                # Save to memory
                self._record_action(page_context.url, action)

                return action

            except (json.JSONDecodeError, ValidationError, Exception) as e:
                logger.warning(f"Brain generation error (attempt {attempt + 1}): {e}")
                if attempt < 2:
                    parts[0] += (
                        f"\n\nERROR: Your previous response was invalid JSON: {e}\nReturn ONLY valid JSON matching the schema."
                    )
                else:
                    return AgentAction(
                        thinking=f"Failed to generate valid action after 3 attempts. Error: {e}",
                        action_type="fail",
                        confidence=0.0,
                        expected_result="Fail safely",
                    )

    def _record_action(self, url: str, action: AgentAction):
        self.conversation_history.append(
            {
                "step": self.action_count,
                "url": url,
                "action": action.model_dump(),
                "timestamp": datetime.now().isoformat(),
            }
        )
        # Keep window small
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)

    async def extract_data(self, content: str, schema: dict) -> dict:
        """
        Extract structured data.
        """
        prompt = f"""
        Extract data from the text based on schema:
        {json.dumps(schema, indent=2)}
        
        Text:
        {content[:15000]}...
        """
        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text.replace("```json", "").replace("```", "")
            return json.loads(text)
        except Exception:
            return {}

    async def score_job(self, job: Any, profile: UserProfileResponse) -> float:
        """
        Score a job (Orchestrator helper).
        """
        prompt = f"""
        Rate job 0.0-1.0 match for user.
        Job: {job.title} at {job.company}
        User Roles: {profile.search_preferences.target_roles}
        Return JSON: {{"score": 0.5}}
        """
        try:
            response = await self.model.generate_content_async(prompt)
            text = response.text.replace("```json", "").replace("```", "")
            return float(json.loads(text).get("score", 0.0))
        except:
            return 0.5
