from typing import Any, Dict, List

from src.agent.brain import AgentBrain
from src.agent.form.detector import FormField


class FormMapper:
    """
    Maps persona data to detected form fields using the Brain (LLM).
    """

    def __init__(self, brain: AgentBrain):
        self.brain = brain

    async def map_fields(
        self, fields: List[FormField], persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Returns a dictionary of {selector: value} to fill.
        """
        if not fields:
            return {}

        fields_schema = [f.model_dump() for f in fields]

        # We ask the brain to generate the mapping
        # We treat this as a data extraction/transformation task
        prompt = f"""
        Map the User Profile data to the Form Fields.
        
        User Profile:
        {persona}
        
        Form Fields:
        {fields_schema}
        
        Return a JSON object where keys are the 'selector' from Form Fields and values are the corresponding values from the Profile.
        
        MAPPING RULES:
        1. 'personal_info' contains basic contact details.
        2. 'application_answers' contains common QA responses (strengths, weaknesses, etc.).
        3. 'search_preferences' might contain location or role preferences.
        4. If a field matches a key in the profile, use it.
        5. For boolean fields (checkboxes), infer from the data (e.g. "relocate": true).
        6. If data is missing, leave the value null.
        """

        # We need a method in Brain that accepts raw prompt for flexibility
        # Temporarily using internal model access or adding a generic method
        response = await self.brain.model.generate_content_async(prompt)

        # Parse JSON from response
        import json

        try:
            # Cleanup markdown code blocks if present
            text = response.text.replace("```json", "").replace("```", "")
            mapping = json.loads(text)
            return mapping
        except Exception:
            return {}
