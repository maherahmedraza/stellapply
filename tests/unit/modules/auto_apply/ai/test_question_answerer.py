import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.modules.auto_apply.ai.question_answerer import QuestionAnswerer, QuestionType
from src.modules.persona.domain.models import Experience, Persona
from src.modules.persona.domain.services import PersonaService


@pytest.fixture
def mock_persona_service():
    return AsyncMock(spec=PersonaService)


@pytest.fixture
def mock_redis():
    with patch("src.modules.auto_apply.ai.question_answerer.redis_provider") as mock:
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock()
        yield mock


@pytest.fixture
def mock_langchain():
    with (
        patch(
            "src.modules.auto_apply.ai.question_answerer.ChatGoogleGenerativeAI"
        ) as mock_llm,
        patch(
            "src.modules.auto_apply.ai.question_answerer.GoogleGenerativeAIEmbeddings"
        ) as mock_emb,
    ):
        # Mock LLM chain
        mock_chain = AsyncMock()
        mock_chain.ainvoke.return_value = "Answer from Gemini"

        # Mock Embeddings
        instance_emb = mock_emb.return_value
        instance_emb.aembed_query = AsyncMock(return_value=[0.1] * 768)

        yield mock_llm, mock_emb


@pytest.fixture
def question_answerer(mock_persona_service, mock_redis, mock_langchain):
    # Ensure fixtures are active (satisfies ARG001)
    _ = mock_redis
    _ = mock_langchain

    # We need to mock the chain creation which happens in __init__
    with (
        patch("src.modules.auto_apply.ai.question_answerer.PromptTemplate"),
        patch("src.modules.auto_apply.ai.question_answerer.StrOutputParser"),
    ):
        qa = QuestionAnswerer(mock_persona_service)
        # Manually set the mock chain to avoid complex LCEL mocking
        qa.chain = AsyncMock()
        qa.chain.ainvoke.return_value = "Answer from Gemini"
        # Mock embeddings instance method
        qa.embeddings.aembed_query = AsyncMock(return_value=[0.1] * 768)

        return qa


@pytest.mark.asyncio
async def test_answer_question_success(
    question_answerer, mock_persona_service, mock_redis
):
    user_id = uuid.uuid4()
    job_context = {
        "id": "job-1",
        "company": "Acme",
        "title": "Dev",
        "requirements": "Python",
    }

    # Mock Persona
    persona = MagicMock(spec=Persona)
    persona.experiences = []
    persona.behavioral_answers = []
    persona.skills = []
    mock_persona_service.get_persona_by_user_id.return_value = persona

    answer = await question_answerer.answer_question(
        "Why do you want to work here?", user_id, job_context
    )

    assert answer == "Answer from Gemini"
    mock_persona_service.get_persona_by_user_id.assert_called_once_with(user_id)
    question_answerer.chain.ainvoke.assert_called_once()
    mock_redis.get.assert_called_once()
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_classify_question_types(question_answerer):
    assert (
        question_answerer.classify_question("Why do you want to join our company?")
        == QuestionType.WHY_COMPANY
    )
    assert (
        question_answerer.classify_question("What is your experience with Python?")
        == QuestionType.EXPERIENCE
    )
    assert (
        question_answerer.classify_question("What are your salary expectations?")
        == QuestionType.SALARY
    )
    assert (
        question_answerer.classify_question("Are you available to start immediately?")
        == QuestionType.AVAILABILITY
    )
    assert (
        question_answerer.classify_question("Do you have a valid visa?")
        == QuestionType.VISA
    )
    assert (
        question_answerer.classify_question("Random custom question")
        == QuestionType.CUSTOM
    )


@pytest.mark.asyncio
async def test_retrieve_context_ranking(question_answerer, mock_persona_service):
    user_id = uuid.uuid4()
    job_context = {"id": "job-1"}

    # Mock Persona with experiences
    persona = MagicMock(spec=Persona)

    exp1 = MagicMock(spec=Experience)
    exp1.job_title = "Senior Dev"
    exp1.company_name = "Tech Corp"
    exp1.description = "Led team"
    exp1.experience_embedding = [0.9] * 768  # High similarity

    exp2 = MagicMock(spec=Experience)
    exp2.job_title = "Junior Dev"
    exp2.company_name = "Startup"
    exp2.description = "Fixed bugs"
    exp2.experience_embedding = [0.1] * 768  # Low similarity

    persona.experiences = [exp1, exp2]
    persona.behavioral_answers = []
    persona.skills = []
    persona.career_preference = None

    mock_persona_service.get_persona_by_user_id.return_value = persona

    await question_answerer.answer_question(
        "Tell me about your experience", user_id, job_context
    )

    call_args = question_answerer.chain.ainvoke.call_args[0][0]
    context = call_args["retrieved_context"]

    assert "Senior Dev" in context
    assert "Junior Dev" in context


@pytest.mark.asyncio
async def test_batch_answer(question_answerer):
    question_answerer.answer_question = AsyncMock(return_value="Batch Answer")

    questions = [{"question": "Q1"}, {"question": "Q2"}]
    user_id = uuid.uuid4()
    job_context = {"id": "job-1"}

    answers = await question_answerer.batch_answer(questions, user_id, job_context)

    assert len(answers) == 2
    assert answers[0] == "Batch Answer"
    assert question_answerer.answer_question.call_count == 2
