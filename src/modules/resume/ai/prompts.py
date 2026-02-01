"""Prompts for AI-powered resume enhancement."""

BULLET_ENHANCEMENT_PROMPT = """
You are an expert resume writer. Enhance this bullet point using the STAR method
(Situation, Task, Action, Result).

Original: {original}
Job Context: {context}

Requirements:
1. Start with a strong action verb.
2. Include quantifiable metrics (percentages, dollar amounts, time saved)
   where possible.
3. Focus on impact and results, not just duties.
4. Keep it under 2 lines.
5. Use industry-relevant keywords.

Return JSON:
{{
    "enhanced": "improved bullet point",
    "action_verb": "verb used",
    "metrics_added": true/false,
    "keywords_included": ["keyword1", "keyword2"],
    "confidence_score": 0.0-1.0
}}
"""

PROFESSIONAL_SUMMARY_PROMPT = """
Create a compelling professional summary for this candidate:

Name: {name}
Years of Experience: {years}
Top Skills: {skills}
Recent Role: {recent_role}
Target Role: {target_role}
Key Achievements: {achievements}

Requirements:
1. 3-4 sentences maximum.
2. Highlight unique value proposition.
3. Include quantified achievements.
4. Align with target role requirements.
5. Use industry terminology.

Return only the summary text, no explanations.
"""

ATS_OPTIMIZATION_PROMPT = """
Optimize the following resume content for the target keywords.
Inject the keywords naturally into the text.

Content: {content}
Target Keywords: {keywords}

Requirements:
1. Maintain the original meaning.
2. Ensure the flow remains professional and natural.
3. Prioritize high-impact keywords.

Return the optimized content text only.
"""

IMPROVEMENT_SUGGESTION_PROMPT = """
Audit this resume and provide high-quality improvement suggestions.

Resume Content: {content}

Requirements:
1. Identify missing information.
2. Suggest better wording for weak sections.
3. Point out formatting or structural issues.
4. Recommend additional skills or certifications based on industry trends.

Return JSON list of suggestions:
{{
    "suggestions": [
        {{
            "section": "section name",
            "issue": "description of the issue",
            "suggestion": "how to improve",
            "priority": "LOW/MEDIUM/HIGH"
        }}
    ]
}}
"""

METRIC_INJECTION_PROMPT = """
Identify potential metrics that could be added to this achievement to make it
more impactful.

Achievement: {achievement}

Requirements:
1. Suggest 2-3 specific metrics (e.g., "Increased sales by X%",
   "Managed a budget of $Y").
2. Ensure the metrics are plausible for the role.

Return the achievement text with placeholders [X%] or [$Y] where metrics
should be injected.
"""
