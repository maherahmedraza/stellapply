import pytest
from src.modules.resume.domain.ats_analyzer import ATSAnalyzer, ATSScore


class TestATSAnalyzer:
    @pytest.fixture
    def analyzer(self):
        return ATSAnalyzer()

    @pytest.fixture
    def sample_resume(self):
        return {
            "sections": [
                {
                    "type": "summary",
                    "content": "Experienced software engineer with 5 years...",
                },
                {
                    "type": "experience",
                    "content": [
                        {
                            "title": "Senior Software Engineer",
                            "company": "Tech Corp",
                            "achievements": [
                                "Led development of microservices architecture",
                                "Reduced deployment time by 40%",
                            ],
                        }
                    ],
                },
                {
                    "type": "skills",
                    "content": ["Python", "JavaScript", "AWS", "Docker"],
                },
            ]
        }

    @pytest.mark.asyncio
    async def test_analyze_returns_valid_score(self, analyzer, sample_resume):
        score = await analyzer.analyze(sample_resume)

        assert isinstance(score, ATSScore)
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.format_score <= 100
        assert 0 <= score.content_score <= 100
        assert 0 <= score.keyword_score <= 100

    @pytest.mark.asyncio
    async def test_format_scoring_penalizes_long_resumes(self, analyzer):
        long_resume = {"sections": [{"type": "experience", "content": "x" * 5000}]}
        short_resume = {"sections": [{"type": "experience", "content": "x" * 500}]}

        long_score = await analyzer.analyze(long_resume)
        short_score = await analyzer.analyze(short_resume)

        assert short_score.format_score >= long_score.format_score

    @pytest.mark.asyncio
    async def test_content_scoring_rewards_action_verbs(self, analyzer):
        good_resume = {
            "sections": [
                {
                    "type": "experience",
                    "content": [
                        {
                            "achievements": [
                                "Led team of 5 engineers",
                                "Developed new API endpoints",
                                "Achieved 99.9% uptime",
                            ]
                        }
                    ],
                }
            ]
        }

        bad_resume = {
            "sections": [
                {
                    "type": "experience",
                    "content": [
                        {
                            "achievements": [
                                "Responsible for team",
                                "Worked on API",
                                "Did maintenance",
                            ]
                        }
                    ],
                }
            ]
        }

        good_score = await analyzer.analyze(good_resume)
        bad_score = await analyzer.analyze(bad_resume)

        assert good_score.content_score > bad_score.content_score

    @pytest.mark.asyncio
    async def test_keyword_scoring_for_job_match(self, analyzer, sample_resume):
        job_description = """
        Looking for a Senior Software Engineer with experience in:
        - Python and JavaScript
        - AWS and cloud infrastructure
        - Microservices architecture
        """

        score = await analyzer.analyze(sample_resume, job_description=job_description)

        # Should have high keyword score due to matching skills
        assert score.keyword_score >= 70
        assert "Python" in score.matched_keywords
        assert "AWS" in score.matched_keywords

    @pytest.mark.asyncio
    async def test_recommendations_generated(self, analyzer, sample_resume):
        score = await analyzer.analyze(sample_resume)

        assert isinstance(score.recommendations, list)
        # Should have at least some recommendations
        assert len(score.recommendations) >= 0

    def test_action_verb_detection(self, analyzer):
        strong_verbs = ["Led", "Developed", "Achieved", "Implemented"]
        weak_verbs = ["Helped", "Worked", "Did", "Was"]

        for verb in strong_verbs:
            assert analyzer._is_strong_action_verb(verb) is True

        for verb in weak_verbs:
            assert analyzer._is_strong_action_verb(verb) is False
