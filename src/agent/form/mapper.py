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
        Map the User Persona data to the Form Fields.
        
        User Persona:
        {persona}
        
        Form Fields:
        {fields_schema}
        
        Return a JSON object where keys are the 'selector' from Form Fields and values are the corresponding values from Persona.
        If a field cannot be filled from persona, ignore it or infer a reasonable default if obvious.
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
