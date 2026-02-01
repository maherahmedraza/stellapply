import json
import logging
import os
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLLM:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY is not set. Using fallback mock logic.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            # Use gemini-flash-latest for stability/speed
            self.model = genai.GenerativeModel("gemini-flash-latest")

    def analyze_resume(self, text: str) -> dict[str, Any]:
        """
        Analyzes resume text using Gemini API.
        Returns ATS score and feedback in JSON format.
        """
        if not self.model:
            return self._mock_fallback(text)

        prompt = f"""
        You are an expert ATS (Applicant Tracking System) implementation.
        Analyze the following resume text and provide a comprehensive evaluation.

        Resume Text:
        {text}

        Your output MUST be a valid JSON object with the following structure:
        {{
            "ats_score": <integer between 0 and 100>,
            "analysis_results": {{
                "summary": "<brief professional summary>",
                "keywords_found": ["<list>", "<of>", "<key>", "<skills>"],
                "feedback": ["<list of feedback>", "<e.g. gaps, formatting>"],
                "missing_keywords": ["<list of missing key terms>"]
            }}
        }}

        Do not include markdown (like ```json), just the raw JSON string.
        """

        try:
            response = self.model.generate_content(prompt)
            # Cleanup potential markdown ticks if model adds them despite instructions
            raw_text = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text)
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return self._mock_fallback(text, error=str(e))

    def _mock_fallback(self, text: str, error: str = None) -> dict[str, Any]:
        """
        Fallback mock logic if API fails or key is missing.
        """
        score = 50
        feedback = ["Using Local Mock Fallback due to API configuration."]
        if error:
            feedback.append(f"Error: {error}")

        keywords = ["python", "go", "react", "sql", "docker"]
        found = [k for k in keywords if k in text.lower()]
        score += len(found) * 10
        score = min(score, 100)

        return {
            "ats_score": score,
            "analysis_results": {
                "summary": "Mock Analysis (Gemini Unavailable)",
                "keywords_found": found,
                "feedback": feedback,
                "missing_keywords": [],
            },
        }


llm_client = GeminiLLM()
