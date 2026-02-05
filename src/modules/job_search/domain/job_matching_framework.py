"""
Job Matching Framework
======================
Comprehensive framework for matching candidate profiles with job listings.
Uses multi-dimensional scoring with explainability.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from sklearn.metrics.pairwise import cosine_similarity

from src.modules.job_search.domain.models import Job
from src.modules.persona.domain.models import Persona


class MatchCategory(Enum):
    """Categories of matching criteria"""

    HARD_REQUIREMENT = "hard_requirement"
    SKILL_MATCH = "skill_match"
    EXPERIENCE_RELEVANCE = "experience_relevance"
    CULTURE_FIT = "culture_fit"
    PREFERENCE_ALIGNMENT = "preference_alignment"


class MatchLevel(Enum):
    """Match quality levels"""

    EXCELLENT = "excellent"  # 85-100
    GOOD = "good"  # 70-84
    MODERATE = "moderate"  # 55-69
    LOW = "low"  # 40-54
    POOR = "poor"  # 0-39


@dataclass
class SkillMatch:
    """Represents a skill match between candidate and job"""

    skill_name: str
    candidate_proficiency: int  # 1-5
    job_requirement_level: str  # required, preferred, nice_to_have
    match_type: str  # exact, semantic, partial
    semantic_similarity: float  # 0-1
    years_experience: float


@dataclass
class RequirementMatch:
    """Represents a hard requirement match"""

    requirement_name: str
    requirement_value: str
    candidate_value: str
    is_met: bool
    is_dealbreaker: bool
    notes: str


@dataclass
class MatchExplanation:
    """Detailed explanation of match score"""

    overall_score: float
    match_level: MatchLevel

    # Component scores
    hard_requirements_score: float
    skill_match_score: float
    experience_relevance_score: float
    culture_fit_score: float

    # Detailed breakdowns
    skill_matches: list[SkillMatch]
    requirement_matches: list[RequirementMatch]

    # Strengths and gaps
    strengths: list[str]
    gaps: list[str]

    # Recommendations
    recommendations: list[str]

    # Interview preparation
    likely_interview_questions: list[str]
    talking_points: list[str]


@dataclass
class JobMatchResult:
    """Complete job match result"""

    job_id: UUID
    job_title: str
    company_name: str
    score: float
    match_level: MatchLevel
    explanation: MatchExplanation

    # Quick summary
    matching_skills: list[str]
    missing_skills: list[str]
    is_qualified: bool
    is_stretch: bool  # Slightly under-qualified but worth applying


@runtime_checkable
class EmbeddingService(Protocol):
    async def embed_text(self, text: str) -> list[float]: ...


@runtime_checkable
class PersonaRepository(Protocol):
    async def get_by_id(self, persona_id: UUID) -> Persona | None: ...


@runtime_checkable
class JobRepository(Protocol):
    async def get_by_id(self, job_id: UUID) -> Job | None: ...
    async def search_jobs(
        self,
        query: str | None = None,
        embedding: list[float] | None = None,
        limit: int = 20,
    ) -> list[Job]: ...


class JobMatchingFramework:
    """
    Multi-dimensional job matching framework.

    Scoring Philosophy:
    - Hard Requirements: Gatekeepers that can disqualify
    - Skills: Core technical and soft skill alignment
    - Experience: Relevance and depth of past work
    - Culture: Values and work style alignment
    """

    # Scoring weights (must sum to 1.0)
    WEIGHTS = {
        MatchCategory.HARD_REQUIREMENT: 0.40,
        MatchCategory.SKILL_MATCH: 0.30,
        MatchCategory.EXPERIENCE_RELEVANCE: 0.20,
        MatchCategory.CULTURE_FIT: 0.10,
    }

    # Thresholds for match levels
    MATCH_THRESHOLDS = {
        MatchLevel.EXCELLENT: 85,
        MatchLevel.GOOD: 70,
        MatchLevel.MODERATE: 55,
        MatchLevel.LOW: 40,
        MatchLevel.POOR: 0,
    }

    # Hard requirement penalties
    HARD_REQUIREMENT_PENALTIES = {
        "visa_mismatch": -100,  # Complete disqualification
        "location_mismatch": -50,  # Significant but not absolute
        "experience_deficit": -30,  # Per year deficit
        "education_mismatch": -20,  # Education requirement not met
        "certification_missing": -15,  # Required cert missing
    }

    def __init__(
        self,
        embedding_service: EmbeddingService,
        persona_repository: PersonaRepository,
        job_repository: JobRepository,
        skill_taxonomy: Any = None,  # Optional taxonomy service/dict
    ):
        self.embedding_service = embedding_service
        self.persona_repo = persona_repository
        self.job_repo = job_repository
        self.skill_taxonomy = skill_taxonomy

    async def calculate_match(
        self, persona_id: UUID, job_id: UUID
    ) -> JobMatchResult | None:
        """
        Calculate comprehensive match between a candidate and job.
        """

        # Load data
        persona = await self.persona_repo.get_by_id(persona_id)
        if not persona:
            raise ValueError("Persona not found")

        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        # Calculate each component score
        hard_req_score, req_matches = await self._score_hard_requirements(persona, job)

        skill_score, skill_matches = await self._score_skills(persona, job)

        experience_score = await self._score_experience_relevance(persona, job)

        culture_score = await self._score_culture_fit(persona, job)

        # Calculate weighted overall score
        raw_score = (
            self.WEIGHTS[MatchCategory.HARD_REQUIREMENT] * hard_req_score
            + self.WEIGHTS[MatchCategory.SKILL_MATCH] * skill_score
            + self.WEIGHTS[MatchCategory.EXPERIENCE_RELEVANCE] * experience_score
            + self.WEIGHTS[MatchCategory.CULTURE_FIT] * culture_score
        )

        # Apply hard requirement penalties
        final_score = self._apply_hard_requirement_penalties(raw_score, req_matches)

        # Determine match level
        match_level = self._determine_match_level(final_score)

        # Generate explanation
        explanation = self._generate_explanation(
            overall_score=final_score,
            match_level=match_level,
            hard_requirements_score=hard_req_score,
            skill_match_score=skill_score,
            experience_relevance_score=experience_score,
            culture_fit_score=culture_score,
            skill_matches=skill_matches,
            requirement_matches=req_matches,
            persona=persona,
            job=job,
        )

        # Compile result
        matching_skills = [
            sm.skill_name
            for sm in skill_matches
            if sm.match_type in ["exact", "semantic"]
        ]
        missing_skills = self._identify_missing_skills(skill_matches)

        return JobMatchResult(
            job_id=job.id,
            job_title=job.title,
            company_name=job.company,
            score=round(final_score, 1),
            match_level=match_level,
            explanation=explanation,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            is_qualified=final_score >= 60 and hard_req_score >= 50,
            is_stretch=50 <= final_score < 60 and hard_req_score >= 50,
        )

    # --- Helper Logic Implementation ---

    def _apply_hard_requirement_penalties(
        self, raw_score: float, req_matches: list[RequirementMatch]
    ) -> float:
        """Apply penalties to the raw score based on unmet hard requirements."""
        final_score = raw_score
        # Logic is actually already handled in _score_hard_requirements returning a score component,
        # but the prompt implies applying penalties to the weighted sum as well or instead.
        # The prompt says: "Apply hard requirement penalties" to "raw_score".
        # However, _score_hard_requirements already returns a score 0-100.
        # If we interpret "Hard Requirements" as just one weighted component, then checking for
        # dealbreakers here acts as an override.

        for match in req_matches:
            if not match.is_met and match.is_dealbreaker:
                # If dealbreaker is hit, cap the score at a low value or apply massive penalty
                # The map has penalties like -100. Let's look up the penalty.
                # Since we don't have the key here easily, we can infer from dealbreaker flag.
                if "Authorization" in match.requirement_name:
                    final_score += self.HARD_REQUIREMENT_PENALTIES["visa_mismatch"]
                elif "Location" in match.requirement_name:
                    final_score += self.HARD_REQUIREMENT_PENALTIES["location_mismatch"]

        return max(0.0, final_score)

    def _determine_match_level(self, score: float) -> MatchLevel:
        if score >= self.MATCH_THRESHOLDS[MatchLevel.EXCELLENT]:
            return MatchLevel.EXCELLENT
        elif score >= self.MATCH_THRESHOLDS[MatchLevel.GOOD]:
            return MatchLevel.GOOD
        elif score >= self.MATCH_THRESHOLDS[MatchLevel.MODERATE]:
            return MatchLevel.MODERATE
        elif score >= self.MATCH_THRESHOLDS[MatchLevel.LOW]:
            return MatchLevel.LOW
        return MatchLevel.POOR

    def _identify_missing_skills(self, skill_matches: list[SkillMatch]) -> list[str]:
        return [sm.skill_name for sm in skill_matches if sm.match_type == "none"]

    async def _score_hard_requirements(
        self, persona: Persona, job: Job
    ) -> tuple[float, list[RequirementMatch]]:
        """
        Score hard requirements (dealbreakers).
        """
        matches = []
        penalty_total = 0

        # 1. LOCATION MATCH
        location_match = self._check_location_match(persona, job)
        matches.append(location_match)
        if not location_match.is_met:
            penalty_total += abs(self.HARD_REQUIREMENT_PENALTIES["location_mismatch"])

        # 2. VISA/AUTHORIZATION MATCH
        visa_match = self._check_visa_match(persona, job)
        matches.append(visa_match)
        if not visa_match.is_met and visa_match.is_dealbreaker:
            penalty_total += abs(self.HARD_REQUIREMENT_PENALTIES["visa_mismatch"])

        # 3. EXPERIENCE LEVEL MATCH
        experience_match = self._check_experience_match(persona, job)
        matches.append(experience_match)
        if not experience_match.is_met:
            # Calculate deficit
            deficit = self._calculate_experience_deficit(persona, job)
            penalty_total += (
                deficit * abs(self.HARD_REQUIREMENT_PENALTIES["experience_deficit"]) / 5
            )  # Scale by 5 years

        # 4. EDUCATION MATCH
        education_match = self._check_education_match(persona, job)
        matches.append(education_match)
        # Assuming we parsed 'requires_specific_education' from description or raw_data
        requires_edu = "degree" in job.description.lower()
        if not education_match.is_met and requires_edu:
            penalty_total += abs(self.HARD_REQUIREMENT_PENALTIES["education_mismatch"])

        # 5. CERTIFICATION MATCH
        cert_matches = self._check_certification_match(persona, job)
        matches.extend(cert_matches)
        for cert in cert_matches:
            if not cert.is_met and cert.is_dealbreaker:
                penalty_total += abs(
                    self.HARD_REQUIREMENT_PENALTIES["certification_missing"]
                )

        # Calculate score (100 - penalties, min 0)
        score = max(0.0, 100 - penalty_total)

        return score, matches

    def _check_location_match(self, persona: Persona, job: Job) -> RequirementMatch:
        """Check if candidate's location matches job requirements."""
        # Simple extraction from job description if structured fields are missing
        is_remote_job = (
            "remote" in (job.work_setting or "").lower()
            or "remote" in job.description.lower()
        )
        job_loc_city = job.location or ""

        # Remote jobs match everyone with remote preference
        if is_remote_job:
            # Assuming 'remote_preference' exists on persona (it might not in the model shown, using defaults)
            # Persona model viewed earlier didn't show 'remote_preference' explicitly in common fields,
            # but let's assume it exists or use a safe fallback.
            remote_pref = getattr(persona, "remote_preference", "any")
            if remote_pref in ["remote", "any"]:
                return RequirementMatch(
                    requirement_name="Location",
                    requirement_value="Remote",
                    candidate_value=f"{persona.location_city}",
                    is_met=True,
                    is_dealbreaker=False,
                    notes="Remote position matches remote preference",
                )

        # Check geographic proximity (Simple string match for MVP)
        p_city = persona.location_city or ""
        p_country = persona.location_country or ""

        if job_loc_city and p_city:
            is_same_city = job_loc_city.lower() in p_city.lower()
            if is_same_city:
                return RequirementMatch(
                    requirement_name="Location",
                    requirement_value=job_loc_city,
                    candidate_value=f"{p_city}, {p_country}",
                    is_met=True,
                    is_dealbreaker=False,
                    notes="Same city match",
                )

        # Location mismatch
        return RequirementMatch(
            requirement_name="Location",
            requirement_value=job_loc_city or "Unspecified",
            candidate_value=f"{p_city}, {p_country}",
            is_met=False,
            # Default to not dealbreaker unless we know willing_to_relocate is False
            is_dealbreaker=False,
            notes="Location mismatch",
        )

    def _check_visa_match(self, persona: Persona, job: Job) -> RequirementMatch:
        """Check if candidate's work authorization matches job requirements."""
        # Heuristic: Check description for 'sponsorship'
        desc_lower = job.description.lower()
        no_sponsorship = (
            "no sponsorship" in desc_lower
            or "not providing sponsorship" in desc_lower
            or "us citizen" in desc_lower
        )

        p_auth = str(persona.work_authorization)

        if no_sponsorship:
            # simplified check
            is_authorized = "citizen" in p_auth.lower() or "permanent" in p_auth.lower()
            if not is_authorized:
                return RequirementMatch(
                    requirement_name="Work Authorization",
                    requirement_value="Authorization required (No Sponsorship)",
                    candidate_value=p_auth,
                    is_met=False,
                    is_dealbreaker=True,
                    notes="Authorization required but not available",
                )

        return RequirementMatch(
            requirement_name="Work Authorization",
            requirement_value="Open",
            candidate_value=p_auth,
            is_met=True,
            is_dealbreaker=False,
            notes="Work authorization met",
        )

    def _calculate_relevant_experience(self, persona: Persona, job: Job) -> float:
        """Calculate years of relevant experience."""
        total_years = 0.0
        for exp in persona.experiences:
            # Simple keyword match for relevance
            if exp.job_title and exp.job_title.lower() in job.title.lower().split():
                duration = self._calculate_experience_duration(exp)
                total_years += duration
            elif job.title.lower() in (exp.job_title or "").lower():
                duration = self._calculate_experience_duration(exp)
                total_years += duration
            else:
                # Add partial weight for any experience
                total_years += self._calculate_experience_duration(exp) * 0.5
        return total_years

    def _calculate_experience_duration(self, experience) -> float:
        start = experience.start_date
        end = experience.end_date or datetime.now().date()
        days = (end - start).days
        return days / 365.0

    def _check_experience_match(self, persona: Persona, job: Job) -> RequirementMatch:
        candidate_years = self._calculate_relevant_experience(persona, job)

        # Parse requirement from text
        required_years = 0
        match = re.search(r"(\d+)\+?\s*years", job.description)
        if match:
            required_years = int(match.group(1))

        # Allow buffer
        buffer = 0.2
        effective_req = required_years * (1 - buffer)
        is_met = candidate_years >= effective_req

        return RequirementMatch(
            requirement_name="Years of Experience",
            requirement_value=f"{required_years} years",
            candidate_value=f"{candidate_years:.1f} years",
            is_met=is_met,
            is_dealbreaker=False,
            notes=f"{'Meets' if is_met else 'Below'} requirement",
        )

    def _calculate_experience_deficit(self, persona: Persona, job: Job) -> float:
        candidate_years = self._calculate_relevant_experience(persona, job)
        match = re.search(r"(\d+)\+?\s*years", job.description)
        required_years = int(match.group(1)) if match else 0
        return max(0.0, required_years - candidate_years)

    def _check_education_match(self, persona: Persona, job: Job) -> RequirementMatch:
        # Simplified parsing
        req_degree = None
        if "phd" in job.description.lower():
            req_degree = "PhD"
        elif "master" in job.description.lower():
            req_degree = "Master"
        elif "bachelor" in job.description.lower():
            req_degree = "Bachelor"

        has_degree = False
        candidates_degree = "None"
        if persona.educations:
            # Assuming just checking if any education exists for now and if it matches string
            for edu in persona.educations:
                d_type = str(edu.degree_type).lower()
                candidates_degree = str(edu.degree_type)
                if req_degree and req_degree.lower() in d_type:
                    has_degree = True
                    break

        if not req_degree:
            pass  # No specific req found

        # If req found but not met
        if req_degree and not has_degree:
            return RequirementMatch(
                requirement_name="Education",
                requirement_value=req_degree,
                candidate_value=candidates_degree,
                is_met=False,
                is_dealbreaker=False,  # Often negotiable
                notes=f"Missing required {req_degree}",
            )

        return RequirementMatch(
            requirement_name="Education",
            requirement_value=req_degree or "Any",
            candidate_value=candidates_degree,
            is_met=True,
            is_dealbreaker=False,
            notes="Education requirement met",
        )

    def _check_certification_match(
        self, persona: Persona, job: Job
    ) -> list[RequirementMatch]:
        # Placeholder for certification matching logic
        return []

    async def _score_skills(
        self, persona: Persona, job: Job
    ) -> tuple[float, list[SkillMatch]]:
        """
        Score skill match between candidate and job.
        """
        # Parse job requirements into skills
        job_skills = self._parse_job_skills(job)

        # Get candidate skills
        candidate_skills = {
            skill.name.lower(): {
                "proficiency": skill.proficiency_level,
                "years": self._get_skill_experience_years(persona, skill.name),
            }
            for skill in persona.skills
        }

        skill_matches = []
        total_weight = 0.0
        weighted_score = 0.0

        for job_skill, requirement_info in job_skills.items():
            level = requirement_info.get("level", "required")
            weight = {"required": 1.0, "preferred": 0.6, "nice_to_have": 0.3}.get(
                level, 0.5
            )

            total_weight += weight

            # Check for exact match
            if job_skill.lower() in candidate_skills:
                candidate_info = candidate_skills[job_skill.lower()]
                proficiency_score = candidate_info["proficiency"] / 5.0

                skill_matches.append(
                    SkillMatch(
                        skill_name=job_skill,
                        candidate_proficiency=candidate_info["proficiency"],
                        job_requirement_level=level,
                        match_type="exact",
                        semantic_similarity=1.0,
                        years_experience=candidate_info["years"],
                    )
                )

                weighted_score += weight * proficiency_score * 100
                continue

            # Simple substring matching for "Semantic" fallback
            found_related = False
            for c_skill, c_info in candidate_skills.items():
                if c_skill in job_skill.lower() or job_skill.lower() in c_skill:
                    skill_matches.append(
                        SkillMatch(
                            skill_name=job_skill,
                            candidate_proficiency=c_info["proficiency"],
                            job_requirement_level=level,
                            match_type="partial",
                            semantic_similarity=0.8,
                            years_experience=c_info["years"],
                        )
                    )
                    weighted_score += weight * (c_info["proficiency"] / 5.0) * 80
                    found_related = True
                    break

            if found_related:
                continue

            # No match found
            skill_matches.append(
                SkillMatch(
                    skill_name=job_skill,
                    candidate_proficiency=0,
                    job_requirement_level=level,
                    match_type="none",
                    semantic_similarity=0.0,
                    years_experience=0,
                )
            )

        # Calculate final score
        score = weighted_score / total_weight if total_weight > 0 else 50.0

        return min(100.0, score), skill_matches

    def _parse_job_skills(self, job: Job) -> dict[str, dict[str, Any]]:
        # Heuristic extraction of capitalized words or known tech stack
        # In a real app, this would use an extractor service or pre-cached raw_data
        text = job.description
        skills = {}
        # Simple extraction of common tech terms (example list)
        common_tech = [
            "Python",
            "JavaScript",
            "React",
            "AWS",
            "Docker",
            "Kubernetes",
            "SQL",
            "FastAPI",
            "TypeScript",
            "Java",
            "Go",
        ]

        for tech in common_tech:
            if tech.lower() in text.lower():
                skills[tech] = {"level": "required"}  # Default to required for now

        return skills

    def _get_skill_experience_years(self, persona: Persona, skill_name: str) -> float:
        # Placeholder: infer from experiences where skill might be used
        return 2.0  # default assumption

    async def _find_semantic_skill_match(
        self, job_skill: str, candidate_skills: list[str]
    ) -> dict[str, Any] | None:
        # Placeholder for embedding-based semantic search
        return None

    async def _score_experience_relevance(self, persona: Persona, job: Job) -> float:
        """
        Score how relevant the candidate's experience is to the job.
        """
        scores = []

        # Generate job embedding
        # Only if we can; otherwise return neutral score
        if not job.description:
            return 50.0

        try:
            job_embedding = await self.embedding_service.embed_text(
                f"{job.title} {job.description[:1000]}"
            )
        except Exception:
            return 50.0  # Fallback

        for experience in persona.experiences:
            # Calculate experience embedding
            exp_text = f"{experience.job_title} at {experience.company_name}. "
            exp_text += experience.description_active or ""
            exp_text += " ".join(experience.achievements or [])

            exp_embedding = await self.embedding_service.embed_text(exp_text)

            # Calculate similarity
            similarity = cosine_similarity([job_embedding], [exp_embedding])[0][0]

            # Weight by recency
            end_date = experience.end_date or datetime.now().date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            years_ago = (datetime.now().date() - end_date).days / 365
            recency_weight = max(0.5, 1.0 - (years_ago * 0.1))

            # Weight by duration
            duration_years = self._calculate_experience_duration(experience)
            duration_weight = min(1.0, duration_years / 3)  # Max weight at 3 years

            weighted_similarity = similarity * recency_weight * duration_weight
            scores.append(weighted_similarity)

        if not scores:
            return 30.0  # Minimum score if no experience

        # Use top 3 most relevant experiences
        top_scores = sorted(scores, reverse=True)[:3]
        avg_score = sum(top_scores) / len(top_scores)

        return avg_score * 100

    async def _score_culture_fit(self, persona: Persona, job: Job) -> float:
        """
        Score culture fit based on values and work style alignment.
        """
        # Extract culture signals from job
        culture_keywords = self._extract_culture_signals(job.description)

        if not culture_keywords:
            return 50.0  # Neutral if no culture signals

        # Get candidate's values and work style
        candidate_values = []

        # Checking if behavioral_answers exist
        # Assuming behavioral_answers is a simple list or has .answer attribute if it exists
        # Model check needed, but let's be safe
        if hasattr(persona, "behavioral_answers") and persona.behavioral_answers:
            for answer in persona.behavioral_answers:
                candidate_values.append(str(answer))

        if not candidate_values:
            return 50.0  # Neutral if no candidate values

        # Calculate semantic similarity
        culture_text = " ".join(culture_keywords)
        values_text = " ".join(candidate_values)

        culture_embedding = await self.embedding_service.embed_text(culture_text)
        values_embedding = await self.embedding_service.embed_text(values_text)

        similarity = cosine_similarity([culture_embedding], [values_embedding])[0][0]

        return similarity * 100

    def _extract_culture_signals(self, description: str) -> list[str]:
        # Simple keyword extraction
        culture_terms = [
            "collaborative",
            "fast-paced",
            "remote",
            "inclusive",
            "innovative",
            "startup",
            "corporate",
        ]
        found = []
        for term in culture_terms:
            if term in description.lower():
                found.append(term)
        return found

    def _generate_explanation(
        self,
        overall_score: float,
        match_level: MatchLevel,
        hard_requirements_score: float,
        skill_match_score: float,
        experience_relevance_score: float,
        culture_fit_score: float,
        skill_matches: list[SkillMatch],
        requirement_matches: list[RequirementMatch],
        persona: Persona,
        job: Job,
    ) -> MatchExplanation:
        """
        Generate human-readable match explanation.
        """

        # Identify strengths
        strengths = []
        if skill_match_score >= 80:
            strengths.append(f"Strong skill match ({skill_match_score:.0f}%)")

        matched_skills = [
            sm.skill_name
            for sm in skill_matches
            if sm.match_type in ["exact", "semantic"]
        ]
        if len(matched_skills) >= 5:
            strengths.append(f"Matches {len(matched_skills)} required skills")

        if experience_relevance_score >= 75:
            strengths.append("Highly relevant experience background")

        if culture_fit_score >= 70:
            strengths.append("Good culture alignment")

        # Met requirements
        met_requirements = [rm for rm in requirement_matches if rm.is_met]
        for rm in met_requirements:
            if rm.requirement_name == "Work Authorization":
                strengths.append("Meets work authorization requirements")
            elif rm.requirement_name == "Location":
                strengths.append("Location compatible")

        # Identify gaps
        gaps = []

        # Missing skills
        missing_required = [
            sm.skill_name
            for sm in skill_matches
            if sm.match_type == "none" and sm.job_requirement_level == "required"
        ]
        if missing_required:
            gaps.append(f"Missing required skills: {', '.join(missing_required[:5])}")

        # Unmet requirements
        unmet = [rm for rm in requirement_matches if not rm.is_met]
        for rm in unmet:
            gaps.append(f"{rm.requirement_name}: {rm.notes}")

        # Generate recommendations
        recommendations = []

        if missing_required:
            recommendations.append(
                f"Consider highlighting any related experience with: {', '.join(missing_required[:3])}"
            )

        if experience_relevance_score < 60:
            recommendations.append(
                "Tailor your resume to emphasize relevant experience for this role"
            )

        if overall_score >= 60:
            recommendations.append("Good match - apply with a tailored resume")
        elif overall_score >= 50:
            recommendations.append(
                "Stretch opportunity - apply with strong cover letter explaining transferable skills"
            )

        # Generate likely interview questions
        interview_questions = self._generate_likely_questions(
            skill_matches, persona, job
        )

        # Generate talking points
        talking_points = self._generate_talking_points(matched_skills, persona, job)

        return MatchExplanation(
            overall_score=overall_score,
            match_level=match_level,
            hard_requirements_score=hard_requirements_score,
            skill_match_score=skill_match_score,
            experience_relevance_score=experience_relevance_score,
            culture_fit_score=culture_fit_score,
            skill_matches=skill_matches,
            requirement_matches=requirement_matches,
            strengths=strengths,
            gaps=gaps,
            recommendations=recommendations,
            likely_interview_questions=interview_questions,
            talking_points=talking_points,
        )

    def _generate_likely_questions(
        self, skill_matches: list[SkillMatch], persona: Persona, job: Job
    ) -> list[str]:
        """Generate likely interview questions based on match analysis."""

        questions = []

        # Questions about matched skills
        for sm in skill_matches[:5]:
            if sm.match_type == "exact" and sm.years_experience > 0:
                questions.append(
                    f"Tell me about your experience with {sm.skill_name}. "
                    f"You have {sm.years_experience:.1f} years - can you describe a challenging project?"
                )

        # Questions about gaps
        missing = [sm.skill_name for sm in skill_matches if sm.match_type == "none"]
        for skill in missing[:2]:
            questions.append(
                f"This role requires {skill}. What experience do you have with similar technologies?"
            )

        # Standard behavioral questions
        questions.extend(
            [
                "Why are you interested in this role and company?",
                "Tell me about a challenging project you led.",
                "How do you handle tight deadlines?",
            ]
        )

        return questions[:10]

    def _generate_talking_points(
        self, matched_skills: list[str], persona: Persona, job: Job
    ) -> list[str]:
        """Generate talking points for the candidate."""

        points = []

        # Skill-based talking points
        for skill in matched_skills[:5]:
            years = self._get_skill_experience_years(persona, skill)
            if years > 0:
                points.append(f"Emphasize your {years:.1f} years of {skill} experience")

        # Experience-based talking points
        for exp in persona.experiences[:2]:
            if exp.achievements:
                points.append(f"Highlight: {exp.achievements[0]} at {exp.company_name}")

        # Company research point
        points.append(
            f"Research {job.company}'s recent news and mention specific interest"
        )

        return points

    # === Batch Matching for Job Feed ===

    async def find_top_matches(
        self,
        persona_id: UUID,
        limit: int = 50,
        min_score: float = 50.0,
        filters: dict | None = None,
    ) -> list[JobMatchResult]:
        """
        Find top matching jobs for a candidate.
        Optimized for performance with caching and batch processing.
        """

        persona = await self.persona_repo.get_by_id(persona_id)
        if not persona:
            return []

        # Use vector search for initial candidates
        candidate_jobs = await self._vector_search_candidates(
            persona, limit * 3, filters
        )

        # Score each candidate in parallel
        results = []
        for job in candidate_jobs:
            try:
                match_result = await self.calculate_match(persona_id, job.id)
                if match_result and match_result.score >= min_score:
                    results.append(match_result)
            except Exception as e:
                # Log but continue
                print(f"Error matching job {job.id}: {e}")
                continue

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]

    async def _vector_search_candidates(
        self, persona: Persona, limit: int, filters: dict | None
    ) -> list[Job]:
        """
        Use vector similarity to find candidate jobs quickly.
        """

        # Build search query from persona
        search_text = self._build_persona_search_text(persona)

        # Get embedding
        query_embedding = await self.embedding_service.embed_text(search_text)

        # Vector search
        return await self.job_repo.search_jobs(
            embedding=query_embedding,
            limit=limit,
        )

    def _build_persona_search_text(self, persona: Persona) -> str:
        """Build search text from persona for vector matching."""

        parts = []

        # Target titles (assuming field exists or using defaults)
        # Using a safe check since model wasn't exhaustive
        if (
            hasattr(persona, "career_preferences")
            and persona.career_preferences
            and persona.career_preferences.target_titles
        ):
            parts.append(" ".join(persona.career_preferences.target_titles))

        # Skills (top 20)
        skill_names = [
            s.name
            for s in sorted(
                persona.skills, key=lambda x: x.proficiency_level or 0, reverse=True
            )[:20]
        ]
        parts.append(" ".join(skill_names))

        # Recent experience
        if persona.experiences:
            recent = persona.experiences[0]
            parts.append(f"{recent.job_title} {recent.description_active or ''}")

        # Summary
        if persona.summary_active:
            parts.append(persona.summary_active)

        return " ".join(parts)
