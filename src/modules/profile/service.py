import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from src.core.config import settings
from src.modules.profile.models import UserProfile
from src.modules.profile.schemas import (
    AgentRulesSchema,
    ApplicationAnswersSchema,
    CertificationSchema,
    EducationSchema,
    ExperienceSchema,
    FullProfile,
    LanguageSchema,
    PersonalInfoSchema,
    ProfileCompletenessReport,
    ResumeStrategySchema,
    SearchPreferencesSchema,
    UserProfileUpdate,
)

logger = logging.getLogger(__name__)

if settings.ai.GEMINI_API_KEY and genai:
    genai.configure(api_key=settings.ai.GEMINI_API_KEY)


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Use a consistent model for extraction
        self.model_name = "gemini-2.0-flash-exp"
        self.model = (
            genai.GenerativeModel(
                self.model_name,
                generation_config={"response_mime_type": "application/json"},
            )
            if genai
            else None
        )

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile:
        """
        Fetch the user's profile DB object. Creates default if none exists.
        """
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalars().first()

        if not profile:
            # Create default profile with empty defaults
            profile = UserProfile(
                user_id=user_id,
                personal_info="{}",
                search_preferences="{}",
                agent_rules="{}",
                application_answers="{}",
                resume_strategy="{}",
                experience="[]",
                education="[]",
                skills="[]",
                languages="[]",
                certifications="[]",
            )
            self.db.add(profile)
            await self.db.commit()
            await self.db.refresh(profile)

        return profile

    async def update_profile(
        self, user_id: uuid.UUID, data: UserProfileUpdate
    ) -> UserProfile:
        """
        Update parts of the profile.
        """
        profile = await self.get_by_user_id(user_id)

        # Helper to dump pydantic to json string or dict depending on column type
        # All extra stats are EncryptedStrings (JSON string) or JSONB (dict)

        if data.personal_info:
            profile.personal_info = data.personal_info.model_dump_json()

        if data.search_preferences:
            profile.search_preferences = data.search_preferences.model_dump()

        if data.agent_rules:
            profile.agent_rules = data.agent_rules.model_dump()

        if data.application_answers:
            profile.application_answers = data.application_answers.model_dump_json()

        if data.resume_strategy:
            profile.resume_strategy = data.resume_strategy.model_dump()

        # New Sections (Encrypted Lists)
        if data.experience is not None:
            profile.experience = json.dumps(
                [x.model_dump(mode="json") for x in data.experience]
            )

        if data.education is not None:
            profile.education = json.dumps(
                [x.model_dump(mode="json") for x in data.education]
            )

        if data.skills is not None:
            profile.skills = json.dumps(data.skills)

        if data.languages is not None:
            profile.languages = json.dumps(
                [x.model_dump(mode="json") for x in data.languages]
            )

        if data.certifications is not None:
            profile.certifications = json.dumps(
                [x.model_dump(mode="json") for x in data.certifications]
            )

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def get_completeness(self, user_id: uuid.UUID) -> ProfileCompletenessReport:
        """
        Calculate profile completeness score based on strict rules.
        """
        profile = await self.get_by_user_id(user_id)

        # Load Data
        def parse_json(val, default):
            return json.loads(val) if val else default

        pi_dict = parse_json(profile.personal_info, {})
        sp_dict = profile.search_preferences or {}
        # ar_dict = profile.agent_rules or {} # Unused
        aa_dict = parse_json(profile.application_answers, {})

        exp_list = parse_json(profile.experience, [])
        edu_list = parse_json(profile.education, [])
        skills_list = parse_json(profile.skills, [])

        # --- Scoring Logic ---
        sections = {}
        missing_critical = []
        recommendations = []

        # 1. Personal Info
        pi_missing = []
        pi_score = 0
        if pi_dict.get("first_name"):
            pi_score += 10
        else:
            pi_missing.append("first_name")
        if pi_dict.get("last_name"):
            pi_score += 10
        else:
            pi_missing.append("last_name")
        if pi_dict.get("email"):
            pi_score += 10
        else:
            pi_missing.append("email")
        if pi_dict.get("phone"):
            pi_score += 10
        else:
            pi_missing.append("phone")
        if pi_dict.get("address"):
            pi_score += 10

        # Normalize to 100
        sections["personal_info"] = {
            "score": min(100, (pi_score / 50) * 100),
            "missing": pi_missing,
        }
        if (
            "first_name" in pi_missing
            or "last_name" in pi_missing
            or "email" in pi_missing
        ):
            missing_critical.append("Personal details")

        # 2. Experience
        exp_score = 100 if len(exp_list) > 0 else 0
        sections["experience"] = {
            "score": exp_score,
            "missing": ["Add at least one experience"] if exp_score == 0 else [],
        }
        if exp_score == 0:
            recommendations.append(
                "Add your work experience to match job requirements."
            )

        # 3. Education
        edu_score = 100 if len(edu_list) > 0 else 0
        sections["education"] = {
            "score": edu_score,
            "missing": ["Add education"] if edu_score == 0 else [],
        }

        # 4. Skills
        skill_score = min(100, len(skills_list) * 10)  # 10 skills = 100%
        sections["skills"] = {
            "score": skill_score,
            "missing": [] if skill_score == 100 else ["Add more skills"],
        }
        if len(skills_list) < 5:
            recommendations.append("Add more skills to improve job matching.")

        # 5. Search Preferences
        sp_missing = []
        sp_score = 0
        if sp_dict.get("target_roles"):
            sp_score += 1
        else:
            sp_missing.append("target_roles")
        if sp_dict.get("locations"):
            sp_score += 1
        else:
            sp_missing.append("locations")
        if sp_dict.get("salary_expectations"):
            sp_score += 1
        else:
            recommendations.append(
                "Set salary expectations to filter jobs effectively."
            )

        sections["search_preferences"] = {
            "score": min(100, (sp_score / 3) * 100),
            "missing": sp_missing,
        }
        if sp_missing:
            missing_critical.extend(sp_missing)

        # 6. Application Answers
        aa_missing = []
        aa_score = 0
        if aa_dict.get("salary_expectation"):
            aa_score += 1
        else:
            aa_missing.append("salary_expectation")
        if aa_dict.get("notice_period"):
            aa_score += 1
        else:
            aa_missing.append("notice_period")

        sections["application_answers"] = {
            "score": min(100, (aa_score / 2) * 100),
            "missing": aa_missing,
        }
        if aa_missing:
            recommendations.append(
                "Fill out common application answers to speed up applying."
            )

        # Overall Calculation (Weighted)
        overall = (
            (sections["personal_info"]["score"] * 0.30)
            + (sections["experience"]["score"] * 0.25)
            + (sections["skills"]["score"] * 0.15)
            + (sections["search_preferences"]["score"] * 0.20)
            + (sections["application_answers"]["score"] * 0.10)
        )

        return ProfileCompletenessReport(
            overall_score=round(overall, 1),
            sections=sections,
            critical_missing=missing_critical,
            recommendations=recommendations,
        )

    async def import_resume(
        self, file_content: bytes, content_type: str
    ) -> FullProfile:
        """
        Use Gemini to extract profile from resume file.
        Returns a FullProfile object (not saved to DB yet) for user review.
        """
        if not self.model:
            raise RuntimeError("Gemini API not configured")

        prompt = """
        You are a detailed Resume Parser. 
        Extract all data from the provided resume and map it EXACTLY to the following JSON structure.
        Ensure dates are in YYYY-MM-DD format. If exact day is missing, use 01.
        
        Structure:
        {
          "personal_info": { "first_name": "...", "last_name": "...", "email": "...", "phone": "...", "address": { "city": "...", "country": "..." }, "linkedin_url": "..." },
          "experience": [ { "company": "...", "title": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "description": "...", "technologies": ["..."] } ],
          "education": [ { "institution": "...", "degree": "...", "field_of_study": "...", "start_date": "YYYY-MM-DD", "graduation_date": "YYYY-MM-DD" } ],
          "skills": [ "..." ],
          "languages": [ { "language": "...", "proficiency": "..." } ],
          "certifications": [ { "name": "...", "issuer": "...", "date_obtained": "YYYY-MM-DD" } ]
        }
        """

        try:
            # Prepare content parts
            parts = [prompt]

            # Map content type to mime type
            mime_type = "application/pdf"  # Default
            if "pdf" in content_type:
                mime_type = "application/pdf"  # Gemini handles PDF extraction natively?
                # Actually Gemini 1.5/2.0 supports document understanding.
                # We need to verify if we can pass bytes directly.
                parts.append({"mime_type": mime_type, "data": file_content})
            else:
                # Text fallback or image
                parts.append({"mime_type": "text/plain", "data": file_content})

            response = await self.model.generate_content_async(parts)
            text = response.text.replace("```json", "").replace("```", "")
            data_dict = json.loads(text)

            # Construct Partial Profile (we default other fields)
            # We return a FullProfile but mostly empty search_prefs etc.

            return FullProfile(
                personal_info=PersonalInfoSchema(**data_dict.get("personal_info", {})),
                experience=[
                    ExperienceSchema(**x) for x in data_dict.get("experience", [])
                ],
                education=[
                    EducationSchema(**x) for x in data_dict.get("education", [])
                ],
                skills=data_dict.get("skills", []),
                languages=[LanguageSchema(**x) for x in data_dict.get("languages", [])],
                certifications=[
                    CertificationSchema(**x)
                    for x in data_dict.get("certifications", [])
                ],
                # Defaults
                search_preferences=SearchPreferencesSchema(
                    target_roles=[], locations=[]
                ),
                agent_rules=AgentRulesSchema(),
                application_answers=ApplicationAnswersSchema(),
                resume_strategy=ResumeStrategySchema(),
            )

        except Exception as e:
            logger.error(f"Resume extraction failed: {e}")
            raise ValueError(f"Failed to extract resume data: {str(e)}")
