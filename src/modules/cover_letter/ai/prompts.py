"""Prompts for AI-powered cover letter generation."""

COVER_LETTER_PROMPT_V1 = """
You are an expert career coach writing a personalized cover letter.

CANDIDATE PROFILE:
{persona_summary}

JOB DETAILS:
Company: {company_name}
Role: {job_title}
Description: {job_description}
Key Requirements: {requirements}

COMPANY RESEARCH:
{company_research}

PREFERENCES:
Tone: {tone}
Length: {length} (Short=150 words, Medium=250 words, Comprehensive=400 words)
Emphasis: {emphasis}

MATCHED QUALIFICATIONS:
{matched_qualifications}

Write a compelling cover letter with:
1. Opening Hook: Why this specific company and role excites the candidate
2. Body: 2-3 paragraphs highlighting the strongest matches between candidate
   and requirements
3. Closing: Clear call to action and enthusiasm

Use the candidate's voice based on their behavioral answers.
Reference specific company values or recent news when available.
Avoid clichés like "I am writing to apply" or "I believe I would be a great fit."

Return the cover letter only, formatted with clear paragraph breaks.
"""

COVER_LETTER_PROMPT_V2 = """
Write a high-impact, modern cover letter for a {job_title} role at {company_name}.

CONTEXT:
Candidate: {persona_summary}
Job Requirements: {requirements}
Company Values: {company_research}

STYLE GUIDE:
Tone: {tone}
Emphasis: {emphasis}
Length: {length}

INSTRUCTIONS:
- Start with a punchy opening that demonstrates industry knowledge.
- Connect 3 specific candidate achievements to the company's current challenges.
- Use a {tone} voice throughout.
- Strictly adhere to the {length} length constraint.
- Eliminate all fluff; focus on "show, don't tell."

Output the cover letter text directly.
"""

REGENERATE_PARAGRAPH_PROMPT = """
Regenerate this specific paragraph from a cover letter based on the guidance provided.

Original Paragraph:
{paragraph}

Guidance:
{guidance}

Context:
Job: {job_title} at {company_name}
Full Content: {full_content}

Maintain the overall tone and flow of the original letter.
"""

ADJUST_TONE_PROMPT = """
Rewrite the following cover letter content to shift the tone to {target_tone}.

Current Content:
{content}

Target Tone: {target_tone}

Requirements:
1. Do not change the core facts or achievements.
2. Adjust vocabulary and sentence structure to match the new tone.
3. Keep the length approximately the same.
"""

GET_ALTERNATIVES_PROMPT = """
Provide {count} alternative versions of this sentence from a cover letter.

Original Sentence:
{sentence}

Requirements:
1. Each alternative should convey the same meaning but with different phrasing.
2. Vary the emphasis and structure.
3. Maintain a professional yet engaging tone.

Return as a JSON list of strings.
"""
