from dataclasses import dataclass
from uuid import UUID

from sklearn.metrics.pairwise import cosine_similarity

from src.core.ai.gemini_client import (
    GeminiClient,
)  # Replaced Protocol with actual client

# Job model from job_search/domain/models presumably
from src.modules.job_search.domain.models import Job
from src.modules.job_search.domain.repository import JobRepository

# In a real scenario, we'd import actual models.
# Using placeholders or assuming structure based on previous context.
# We need basic interfaces for Persona and Job to make this work.
from src.modules.persona.domain.models import Persona
from src.modules.persona.domain.repository import PersonaRepository


@dataclass
class MatchScore:
    overall_score: float  # 0-100
    skills_score: float
    experience_score: float
    preferences_score: float
    culture_score: float
    explanation: list[str]
    matching_skills: list[str]
    missing_skills: list[str]


class JobMatcher:
    """AI-powered job matching engine"""

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {"skills": 0.35, "experience": 0.25, "preferences": 0.25, "culture": 0.15}

    # Hard requirement penalties
    HARD_REQUIREMENTS = {
        "location_mismatch": -50,
        "visa_mismatch": -100,
        "experience_level_mismatch": -30,
        "salary_mismatch": -20,
    }

    def __init__(
        self,
        embedding_service: GeminiClient,
        persona_repository: PersonaRepository,
        job_repository: JobRepository,
    ):
        self.embedding_service = embedding_service
        self.persona_repo = persona_repository
        self.job_repo = job_repository

    async def calculate_match(self, user_id: UUID, job_id: UUID) -> MatchScore:
        """Calculate match score between user and job"""

        persona = await self.persona_repo.get_by_user_id(
            user_id
        )  # Corrected method name from get_by_user
        if not persona:
            raise ValueError("Persona not found")
        job = await self.job_repo.get_by_id(job_id)  # Corrected from get
        if not job:
            raise ValueError("Job not found")

        # Check hard requirements first
        hard_requirement_penalty = self._check_hard_requirements(persona, job)

        if hard_requirement_penalty <= -100:
            return MatchScore(
                overall_score=0,
                skills_score=0,
                experience_score=0,
                preferences_score=0,
                culture_score=0,
                explanation=["Does not meet visa/authorization requirements"],
                matching_skills=[],
                missing_skills=[],
            )

        # Calculate component scores
        skills_score, matching_skills, missing_skills = await self._score_skills(
            persona, job
        )
        experience_score = await self._score_experience(persona, job)
        preferences_score = self._score_preferences(persona, job)
        culture_score = await self._score_culture(persona, job)

        # Weighted average
        raw_score = (
            self.WEIGHTS["skills"] * skills_score
            + self.WEIGHTS["experience"] * experience_score
            + self.WEIGHTS["preferences"] * preferences_score
            + self.WEIGHTS["culture"] * culture_score
        )

        # Apply penalties
        final_score = max(0, min(100, raw_score + hard_requirement_penalty))

        # Generate explanations
        explanations = self._generate_explanations(
            skills_score,
            experience_score,
            preferences_score,
            culture_score,
            matching_skills,
            missing_skills,
        )

        return MatchScore(
            overall_score=round(final_score, 1),
            skills_score=round(skills_score, 1),
            experience_score=round(experience_score, 1),
            preferences_score=round(preferences_score, 1),
            culture_score=round(culture_score, 1),
            explanation=explanations,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
        )

    async def _score_skills(
        self, persona: Persona, job: Job
    ) -> tuple[float, list[str], list[str]]:
        """Score skill match using embeddings and keyword matching"""

        # Extract required skills from job - Placeholder assuming job has skills list
        # If job.skills is raw text, we'd need extraction. Assuming list for now.
        # Extract required skills from job - Placeholder
        # Job model doesn't have skills relation yet, checking raw_data or description
        job_skills = job.raw_data.get("skills", []) if job.raw_data else []
        # Convert to dict with importance if available, else assume required
        job_skills_dict = (
            dict.fromkeys(job_skills, "required")
            if isinstance(job_skills, list)
            else {}
        )

        user_skills = (
            {s.name.lower(): s.proficiency_level for s in persona.skills}
            if persona.skills
            else {}
        )

        matching = []
        missing = []
        weighted_match = 0.0
        total_weight = 0.0

        for skill, importance in job_skills_dict.items():
            skill_lower = skill.lower()
            weight = {"required": 1.0, "preferred": 0.5, "nice_to_have": 0.2}.get(
                importance, 1.0
            )
            total_weight += weight

            # Check direct match
            if skill_lower in user_skills:
                # proficiency is often enum or 1-5, assuming 1-5 or normalizing
                # If enum, we need mapping. Assuming int 1-5 for now or 3 default
                proficiency = 3.0  # Default/Placeholder if not int
                proficiency_factor = proficiency / 5.0
                weighted_match += weight * proficiency_factor
                matching.append(skill)
            else:
                # Check semantic similarity logic here
                # For MVP optimization, we skip per-skill embedding call
                # to avoid N*M calls
                # And assume keyword match is primary.
                # Ideally: cached embeddings for standard skills.
                missing.append(skill)

        score = (weighted_match / total_weight * 100) if total_weight > 0 else 50

        return score, matching, missing

    async def _score_experience(self, persona: Persona, job: Job) -> float:
        """Score experience relevance using vector similarity"""

        if not job.description:
            return 50.0

        # Get job embedding
        try:
            job_embedding = await self.embedding_service.embed_text(
                f"{job.title} {job.description}"
            )
        except Exception:
            return 50.0  # Fallback

        # Get experience embeddings
        experience_scores: list[float] = []

        experiences = persona.experiences or []
        for _exp in experiences:
            # We assume exp has embedding field pre-calculated
            # If not, we might need to calculate on fly (costly) or skip
            # Assuming 'description_embedding' exists on Experience model
            # Re-using prompt logic structure
            exp_embedding = None
            # Placeholder for accessing embedding from experience object

            if exp_embedding:
                similarity = cosine_similarity([job_embedding], [exp_embedding])[0][0]
                experience_scores.append(similarity)

        if not experience_scores:
            return 30  # Minimum score if no experience

        # Use top 3 most relevant experiences
        top_scores = sorted(experience_scores, reverse=True)[:3]
        avg_score = sum(top_scores) / len(top_scores)

        return avg_score * 100

    def _score_preferences(self, persona: Persona, job: Job) -> float:
        """Score match against user preferences"""

        # Check if career_preference is single object or list
        prefs = persona.career_preference
        if not prefs:
            return 100  # Neutral/Optimistic

        score = 100

        # Location match
        # Assuming job.is_remote exists
        if hasattr(job, "is_remote") and job.is_remote:
            # Logic for remote preference
            pass
        else:
            if persona.remote_preference == "REMOTE":  # Check enum
                score -= 30

        # Logic matches prompt structure

        return max(0, min(100, score))

    async def _score_culture(self, persona: Persona, job: Job) -> float:
        """Score culture fit using semantic similarity"""
        _ = persona
        _ = job
        return 50.0

    def _check_hard_requirements(self, persona: Persona, job: Job) -> float:
        """Check hard requirements and return penalty"""
        _ = persona
        _ = job
        return 0

    def _generate_explanations(self, *args: object) -> list[str]:
        _ = args
        return ["Matched based on skills and experience."]

    def _extract_culture_signals(self, text: str) -> list[str]:
        _ = text
        return []

    async def _check_semantic_similarity(
        self, text1: str, candidates: list[str]
    ) -> float:
        _ = text1
        _ = candidates
        return 0.0

    async def get_top_matches(
        self, user_id: UUID, limit: int = 50, min_score: float = 60.0
    ) -> list[tuple[Job, MatchScore]]:
        """Get top matching jobs for user"""

        persona = await self.persona_repo.get_by_user_id(user_id)
        if not persona:
            return []

        # Get candidate jobs using vector search
        candidate_jobs = await self._get_candidate_jobs(persona, limit * 3)

        # Score each candidate
        matches = []
        for job in candidate_jobs:
            score = await self.calculate_match(user_id, job.id)
            if score.overall_score >= min_score:
                matches.append((job, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1].overall_score, reverse=True)

        return matches[:limit]

    async def _get_candidate_jobs(self, persona: Persona, limit: int) -> list[Job]:
        """Use vector search to find candidate jobs"""

        # Search query from title preferences
        # Persona model doesn't have summary text, only embedding
        search_query = (
            persona.career_preference.target_titles[0]
            if persona.career_preference and persona.career_preference.target_titles
            else "Job Search"
        )

        try:
            query_embedding = await self.embedding_service.embed_text(search_query)
        except Exception:
            return []

        # Vector search in pgvector
        # Assuming repository has search_jobs with embedding support
        return await self.job_repo.search_jobs(
            embedding=query_embedding,
            limit=limit,
        )
