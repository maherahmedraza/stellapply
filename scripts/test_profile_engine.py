import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import json

from src.modules.profile.service import ProfileService
from src.modules.profile.models import UserProfile
from src.modules.profile.schemas import FullProfile


class TestProfileEngine(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_db = AsyncMock()
        self.service = ProfileService(self.mock_db)
        self.user_id = uuid.uuid4()

    async def test_completeness_scoring(self):
        """Test completeness logic with a mock profile."""
        # Create a mock profile with specific data
        mock_profile = MagicMock(spec=UserProfile)
        mock_profile.user_id = self.user_id

        # Populate fields (simulating encrypted strings)
        mock_profile.personal_info = json.dumps(
            {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "1234567890",
                "address": {"city": "Berlin"},
            }
        )
        mock_profile.search_preferences = {
            "target_roles": ["Developer"],
            "locations": ["Remote"],
        }
        mock_profile.agent_rules = {}
        mock_profile.application_answers = json.dumps(
            {"salary_expectation": "80k", "notice_period": "3 months"}
        )
        # Empty lists for new sections
        mock_profile.experience = "[]"
        mock_profile.education = "[]"
        mock_profile.skills = "[]"
        mock_profile.languages = "[]"
        mock_profile.certifications = "[]"

        # Mock database return
        self.service.get_by_user_id = AsyncMock(return_value=mock_profile)

        # Run calculation
        report = await self.service.get_completeness(self.user_id)

        print(f"\nCompleteness Report: {report.overall_score}%")
        print(f"Missing Critical: {report.critical_missing}")
        print(f"Recommendations: {report.recommendations}")

        # Assertions
        # Personal Info: 5/5 -> 100%
        # Experience: 0 -> 0%
        # Skills: 0 -> 0%
        # Search Prefs: 2/3 (missing salary) -> 66%
        # App Answers: 2/2 -> 100%

        # Expected:
        # (100 * 0.3) + (0 * 0.25) + (0 * 0.15) + (66.6 * 0.2) + (100 * 0.1)
        # 30 + 0 + 0 + 13.3 + 10 = 53.3

        self.assertAlmostEqual(report.sections["personal_info"]["score"], 100.0)
        self.assertEqual(report.sections["experience"]["score"], 0)
        self.assertGreater(report.overall_score, 40.0)
        self.assertIn(
            "Add at least one experience", report.sections["experience"]["missing"]
        )

    @patch("src.modules.profile.service.genai")
    async def test_resume_import(self, mock_genai):
        """Test resume import using mocked Gemini response."""
        # Setup Mock Gemini
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # Re-init service to pick up mock
        service = ProfileService(self.mock_db)

        # Mock Response
        mock_response = AsyncMock()
        mock_response.text = json.dumps(
            {
                "personal_info": {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "email": "brief@example.com",
                    "phone": "+1234567890",
                },
                "experience": [
                    {"company": "TechCorp", "title": "Dev", "start_date": "2020-01-01"}
                ],
                "skills": ["Python", "AI"],
            }
        )
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        # Call import
        result = await service.import_resume(b"fake pdf content", "application/pdf")

        print(f"\nImported Profile: {result.personal_info.first_name}")

        self.assertIsInstance(result, FullProfile)
        self.assertEqual(result.personal_info.first_name, "Jane")
        self.assertEqual(result.experience[0].company, "TechCorp")
        self.assertEqual(len(result.skills), 2)


if __name__ == "__main__":
    unittest.main()
