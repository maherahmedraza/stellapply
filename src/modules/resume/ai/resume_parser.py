"""
Resume Parser using Gemini AI.

Extracts structured resume data from PDF and DOCX files.
"""

import io
import logging
from typing import Any

from pydantic import BaseModel, Field

from src.core.ai.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class ExtractedExperience(BaseModel):
    """Extracted work experience entry."""

    company: str
    job_title: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_current: bool = False
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)


class ExtractedEducation(BaseModel):
    """Extracted education entry."""

    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None


class ExtractedResume(BaseModel):
    """Complete extracted resume structure."""

    full_name: str
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    website_url: str | None = None
    professional_summary: str | None = None
    experiences: list[ExtractedExperience] = Field(default_factory=list)
    education: list[ExtractedEducation] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


RESUME_EXTRACTION_PROMPT = """
Analyze the following resume text and extract all information into a structured format.
Be thorough and extract every piece of information you can find.

Resume Content:
{content}

Extract the following:
1. Contact Information: name, email, phone, location, LinkedIn, website
2. Professional Summary: any summary or objective statement
3. Work Experience: for each job include company, title, dates, achievements
4. Education: institution, degree, field of study, dates, GPA if present
5. Skills: both technical and soft skills
6. Certifications: any professional certifications
7. Languages: spoken languages

For dates, use formats like "Jan 2020" or "2020-01" when possible.
For current positions, set is_current to true and leave end_date empty.
"""


class ResumeParser:
    """
    Service to parse resume files using Gemini AI.

    Supports PDF and DOCX extraction with multimodal capabilities.
    """

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using pypdf."""
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except ImportError:
            logger.warning("pypdf not installed, using AI extraction")
            return ""
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            return ""

    async def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX."""
        try:
            from docx import Document

            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except ImportError:
            logger.warning("python-docx not installed")
            return ""
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            return ""

    async def parse_resume(self, file_content: bytes, filename: str) -> ExtractedResume:
        """
        Parse resume from PDF or DOCX file.

        Uses text extraction first, falls back to Gemini vision if needed.
        """
        file_ext = filename.lower().split(".")[-1]

        # Extract text based on file type
        if file_ext == "pdf":
            text_content = await self.extract_text_from_pdf(file_content)
        elif file_ext in ("docx", "doc"):
            text_content = await self.extract_text_from_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

        if not text_content:
            # Fallback: use Gemini's multimodal capabilities
            logger.info("Using Gemini vision for resume parsing")
            text_content = await self._extract_with_vision(file_content, file_ext)

        # Use Gemini to structure the extracted text
        return await self._structure_resume(text_content)

    async def _extract_with_vision(self, file_content: bytes, file_type: str) -> str:
        """Use Gemini's vision capabilities to extract text from resume."""
        import base64

        encoded = base64.b64encode(file_content).decode()
        mime_type = "application/pdf" if file_type == "pdf" else "image/*"

        prompt = """
        Extract all text from this resume document.
        Return the raw text content, preserving the structure and formatting.
        Include all sections: contact info, summary, experience, education, skills.
        """

        try:
            result = await self.client.generate_with_image(prompt, encoded, mime_type)
            return result
        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            return ""

    async def _structure_resume(self, text_content: str) -> ExtractedResume:
        """Use Gemini to extract structured data from resume text."""
        if not text_content:
            return ExtractedResume(full_name="Unknown")

        prompt = RESUME_EXTRACTION_PROMPT.format(content=text_content)

        try:
            result = await self.client.generate_structured(prompt, ExtractedResume)
            return result
        except Exception as e:
            logger.error(f"Resume structuring failed: {e}")
            # Return minimal data if extraction fails
            return ExtractedResume(full_name="Resume Owner")

    def convert_to_form_data(self, extracted: ExtractedResume) -> dict[str, Any]:
        """
        Convert extracted resume to form-compatible format.

        This format matches the frontend ResumeForm expectations.
        """
        return {
            "personal_info": {
                "full_name": extracted.full_name,
                "email": extracted.email,
                "phone": extracted.phone,
                "location": extracted.location,
                "linkedin": extracted.linkedin_url,
                "website": extracted.website_url,
            },
            "professional_summary": extracted.professional_summary or "",
            "experiences": [
                {
                    "company": exp.company,
                    "job_title": exp.job_title,
                    "location": exp.location,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "achievements": exp.achievements,
                }
                for exp in extracted.experiences
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree,
                    "field_of_study": edu.field_of_study,
                    "start_date": edu.start_date,
                    "end_date": edu.end_date,
                    "gpa": edu.gpa,
                }
                for edu in extracted.education
            ],
            "skills": extracted.skills,
            "certifications": extracted.certifications,
            "languages": extracted.languages,
        }
