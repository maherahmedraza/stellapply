import hashlib
import logging
import os
from enum import Enum
from typing import Any, cast
from uuid import UUID

import numpy as np
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.core.infrastructure.redis import redis_provider
from src.modules.persona.domain.models import Persona
from src.modules.persona.domain.services import PersonaService

logger = logging.getLogger(__name__)


class QuestionType(Enum):
    WHY_COMPANY = "why_company"
    WHY_ROLE = "why_role"
    EXPERIENCE = "experience"
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    SALARY = "salary"
    AVAILABILITY = "availability"
    VISA = "visa"
    CUSTOM = "custom"


RETRIEVAL_CONFIG = {
    QuestionType.BEHAVIORAL: {
        "sources": ["behavioral_answers", "experiences"],
        "top_k": 3,
        "min_similarity": 0.7,
    },
    QuestionType.EXPERIENCE: {
        "sources": ["experiences", "skills"],
        "top_k": 5,
        "min_similarity": 0.6,
    },
    QuestionType.WHY_COMPANY: {
        "sources": ["career_preference", "experiences"],
        "top_k": 2,
        "min_similarity": 0.5,
    },
    QuestionType.WHY_ROLE: {
        "sources": ["experiences", "skills", "career_preference"],
        "top_k": 3,
        "min_similarity": 0.6,
    },
    QuestionType.TECHNICAL: {
        "sources": ["skills", "experiences"],
        "top_k": 5,
        "min_similarity": 0.7,
    },
    QuestionType.SALARY: {
        "sources": ["career_preference"],
        "top_k": 1,
        "min_similarity": 0.0,
    },
    QuestionType.AVAILABILITY: {
        "sources": [],  # Usually static or computed
        "top_k": 0,
        "min_similarity": 0.0,
    },
    QuestionType.VISA: {
        "sources": ["work_authorization"],
        "top_k": 1,
        "min_similarity": 0.0,
    },
    QuestionType.CUSTOM: {
        "sources": ["experiences", "skills", "behavioral_answers"],
        "top_k": 3,
        "min_similarity": 0.5,
    },
}

QUESTION_ANSWER_PROMPT = """
You are the candidate filling out a job application. Answer naturally in first person.

QUESTION: {question}
CHARACTER LIMIT: {char_limit}

YOUR RELEVANT BACKGROUND:
{retrieved_context}

JOB CONTEXT:
Company: {company}
Role: {role}
Key Requirements: {requirements}

GUIDELINES:
1. Answer specifically and directly
2. Use examples from your actual experience
3. Stay within character limit
4. Sound authentic, not AI-generated
5. Match the question's level of formality
6. If unsure, provide a thoughtful general answer rather than making things up

ANSWER:
"""


class QuestionAnswerer:
    def __init__(self, persona_service: PersonaService):
        self._persona_service = persona_service
        self._api_key = os.getenv("GOOGLE_GEMINI_KEY")
        if not self._api_key:
            logger.warning("GOOGLE_GEMINI_KEY not set. RAG service will fail.")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.0-flash", google_api_key=self._api_key, temperature=0.4
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(  # type: ignore[call-arg]
            model="models/text-embedding-004",
            google_api_key=self._api_key,
        )
        self.chain = (
            PromptTemplate.from_template(QUESTION_ANSWER_PROMPT)
            | self.llm
            | StrOutputParser()
        )

    async def answer_question(
        self,
        question: str,
        user_id: UUID,
        job_context: dict[str, Any],
        char_limit: int = 1000,
    ) -> str:
        """
        Generates an answer for a specific question using RAG.
        """
        # 1. Check Cache
        cached = await self.get_cached_answer(question, user_id, job_context.get("id"))
        if cached:
            return cached

        # 2. Get Persona
        persona = await self._persona_service.get_persona_by_user_id(user_id)
        if not persona:
            raise ValueError(f"Persona not found for user {user_id}")

        # 3. Classify & Retrieve
        q_type = self.classify_question(question)
        context = await self._retrieve_context(question, q_type, persona)

        # 4. Generate
        try:
            response = await self.chain.ainvoke(
                {
                    "question": question,
                    "char_limit": str(char_limit),
                    "retrieved_context": context,
                    "company": job_context.get("company", "Unknown Company"),
                    "role": job_context.get("title", "Unknown Role"),
                    "requirements": job_context.get("requirements", ""),
                }
            )

            # 5. Cache
            await self._cache_answer(question, user_id, job_context.get("id"), response)
            return response

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return (
                "I am excited about this opportunity and believe my skills align "
                "well with the requirements."
            )

    async def batch_answer(
        self,
        questions: list[dict[str, Any]],
        user_id: UUID,
        job_context: dict[str, Any],
    ) -> list[str]:
        """Answers a list of questions concurrently."""
        results = []
        for q_data in questions:
            q_text = q_data.get("question", "")
            limit = q_data.get("limit", 1000)
            answer = await self.answer_question(q_text, user_id, job_context, limit)
            results.append(answer)
        return results

    def classify_question(self, question: str) -> QuestionType:
        """Simple keyword-based classification. Can be upgraded to LLM-based."""
        q_lower = question.lower()
        if "company" in q_lower or "why us" in q_lower:
            return QuestionType.WHY_COMPANY
        if "role" in q_lower or "position" in q_lower or "why this" in q_lower:
            return QuestionType.WHY_ROLE
        if "experience" in q_lower or "background" in q_lower or "years" in q_lower:
            return QuestionType.EXPERIENCE
        if "tell me about a time" in q_lower or "describe a" in q_lower:
            return QuestionType.BEHAVIORAL
        if "technical" in q_lower or "code" in q_lower or "stack" in q_lower:
            return QuestionType.TECHNICAL
        if "salary" in q_lower or "compensation" in q_lower or "pay" in q_lower:
            return QuestionType.SALARY
        if "start" in q_lower or "notice" in q_lower or "available" in q_lower:
            return QuestionType.AVAILABILITY
        if "visa" in q_lower or "sponsorship" in q_lower or "citizen" in q_lower:
            return QuestionType.VISA
        return QuestionType.CUSTOM

    async def get_cached_answer(
        self, question: str, user_id: UUID, job_id: str | None
    ) -> str | None:
        if not job_id:
            return None
        key = self._generate_cache_key(question, user_id, job_id)
        result = await redis_provider.get(key)
        return cast(str | None, result)

    async def _cache_answer(
        self, question: str, user_id: UUID, job_id: str | None, answer: str
    ) -> None:
        if not job_id:
            return
        key = self._generate_cache_key(question, user_id, job_id)
        await redis_provider.set(key, answer, expire=604800)  # 7 days

    def _generate_cache_key(self, question: str, user_id: UUID, job_id: str) -> str:
        q_hash = hashlib.md5(question.encode()).hexdigest()
        return f"answer:{user_id}:{job_id}:{q_hash}"

    async def _retrieve_context(
        self, question: str, q_type: QuestionType, persona: Persona
    ) -> str:
        """Retrieves and formats relevant context from the persona."""
        config: dict[str, Any] = RETRIEVAL_CONFIG.get(
            q_type, RETRIEVAL_CONFIG[QuestionType.CUSTOM]
        )
        sources: list[str] = cast(list[str], config["sources"])
        top_k: int = cast(int, config["top_k"])

        context_parts = []

        # In-memory vector search for small personal datasets
        # Generate question embedding
        q_embedding = await self.embeddings.aembed_query(question)

        candidates: list[dict[str, Any]] = []

        if "experiences" in sources:
            for exp in persona.experiences:
                if exp.experience_embedding is not None:
                    # Cast to numpy for calculation
                    emb = np.array(exp.experience_embedding)
                    sim = self._cosine_similarity(q_embedding, emb)
                    candidates.append(
                        {
                            "text": (
                                f"Experience: {exp.job_title} at {exp.company_name}. "
                                f"{exp.description}"
                            ),
                            "score": sim,
                            "type": "experience",
                        }
                    )
                else:
                    # Fallback if no embedding
                    candidates.append(
                        {
                            "text": (
                                f"Experience: {exp.job_title} at {exp.company_name}. "
                                f"{exp.description}"
                            ),
                            "score": 0.5,  # Default relevancy
                            "type": "experience",
                        }
                    )

        if "behavioral_answers" in sources:
            for ans in persona.behavioral_answers:
                if ans.answer_embedding is not None:
                    emb = np.array(ans.answer_embedding)
                    sim = self._cosine_similarity(q_embedding, emb)
                    candidates.append(
                        {
                            "text": (
                                f"Behavioral Example ({ans.question_type}): "
                                f"{ans.answer}"
                            ),
                            "score": sim,
                            "type": "behavioral",
                        }
                    )

        if "skills" in sources:
            skills_text = ", ".join(
                [f"{s.name} ({s.proficiency_level}/5)" for s in persona.skills]
            )
            context_parts.append(f"Skills: {skills_text}")

        if "career_preference" in sources and persona.career_preference:
            pref = persona.career_preference
            context_parts.append(
                f"Career Goals: Seeking {', '.join(pref.target_titles)} roles. "
                f"Preferred industries: {', '.join(pref.target_industries)}."
            )

        if "work_authorization" in sources:
            context_parts.append(f"Work Authorization: {persona.work_authorization}")

        # Sort and select top K candidates
        candidates.sort(key=lambda x: cast(float, x["score"]), reverse=True)
        selected = candidates[:top_k]

        for item in selected:
            context_parts.append(item["text"])

        if not context_parts:
            return "No specific relevant background found in persona."

        return "\n\n".join(context_parts)

    def _cosine_similarity(self, v1: list[float], v2: Any) -> float:
        vec2 = np.array(v2) if isinstance(v2, list) else np.array(v2)
        vec1 = np.array(v1)

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2) / (norm1 * norm2))
