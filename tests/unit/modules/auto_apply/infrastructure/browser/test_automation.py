from unittest.mock import AsyncMock, patch

import pytest
from playwright.async_api import Browser, BrowserContext, Page, Playwright

from src.modules.auto_apply.infrastructure.browser.automation import (
    STEALTH_CONFIG,
    ATSPlatform,
    BrowserAutomation,
)


@pytest.fixture
def mock_playwright():
    with patch(
        "src.modules.auto_apply.infrastructure.browser.automation.async_playwright"
    ) as mock:
        # Mock Playwright object hierarchy
        playwright_obj = AsyncMock(spec=Playwright)
        browser_obj = AsyncMock(spec=Browser)
        context_obj = AsyncMock(spec=BrowserContext)
        page_obj = AsyncMock(spec=Page)

        # Configure async methods explicitly
        # 1. async_playwright().start() must be awaitable and return playwright_obj
        mock.return_value.start = AsyncMock(return_value=playwright_obj)

        # 2. chromium.launch() must be awaitable and return browser_obj
        playwright_obj.chromium.launch = AsyncMock(return_value=browser_obj)

        # 3. browser.new_context() must be awaitable and return context_obj
        browser_obj.new_context = AsyncMock(return_value=context_obj)

        # 4. context.new_page() must be awaitable and return page_obj
        context_obj.new_page = AsyncMock(return_value=page_obj)

        # Configure nested async methods on Page
        # These need to be AsyncMocks so they can be awaited
        page_obj.keyboard.type = AsyncMock()
        page_obj.mouse.wheel = AsyncMock()
        page_obj.mouse.move = AsyncMock()
        page_obj.evaluate = AsyncMock(return_value=1000)
        page_obj.wait_for_selector = AsyncMock()
        page_obj.goto = AsyncMock()
        page_obj.screenshot = AsyncMock(return_value=b"screenshot")

        # Setup page properties (sync attributes)
        page_obj.url = "https://boards.greenhouse.io/acme/jobs/123"

        yield mock


@pytest.fixture
def automation(mock_playwright):
    _ = mock_playwright  # Ensure fixture is used
    return BrowserAutomation(headless=True)


@pytest.mark.asyncio
async def test_start_browser(automation, mock_playwright):
    await automation.start()

    # Verify Playwright started
    mock_playwright.return_value.start.assert_called_once()

    # Verify Chromium launch with args
    playwright_obj = mock_playwright.return_value.start.return_value
    playwright_obj.chromium.launch.assert_called_once()

    call_kwargs = playwright_obj.chromium.launch.call_args[1]
    assert call_kwargs["headless"] is True
    assert "--disable-blink-features=AutomationControlled" in call_kwargs["args"]


@pytest.mark.asyncio
async def test_create_context_with_stealth(automation, mock_playwright):
    await automation.create_context()

    playwright_obj = mock_playwright.return_value.start.return_value
    browser_obj = playwright_obj.chromium.launch.return_value

    # Verify context creation with stealth config
    browser_obj.new_context.assert_called_once()
    call_kwargs = browser_obj.new_context.call_args[1]

    assert call_kwargs["user_agent"] == STEALTH_CONFIG["user_agent"]
    assert call_kwargs["viewport"] == STEALTH_CONFIG["viewport"]

    # Verify init script injection
    context_obj = browser_obj.new_context.return_value
    context_obj.add_init_script.assert_called_once()


@pytest.mark.asyncio
async def test_navigate_to_job(automation):
    page = await automation.navigate_to_job("https://example.com/job")

    assert page is not None
    page.goto.assert_called_with(
        "https://example.com/job", wait_until="domcontentloaded", timeout=60000
    )


@pytest.mark.asyncio
async def test_detect_ats_platform(automation):
    # Mock Page
    page = AsyncMock(spec=Page)

    page.url = "https://boards.greenhouse.io/job/123"
    assert automation.detect_ats_platform(page) == ATSPlatform.GREENHOUSE

    page.url = "https://jobs.lever.co/acme/123"
    assert automation.detect_ats_platform(page) == ATSPlatform.LEVER

    page.url = "https://acme.wd5.myworkdayjobs.com/en-US/careers"
    assert automation.detect_ats_platform(page) == ATSPlatform.WORKDAY

    page.url = "https://company.bamboohr.com/jobs"
    assert automation.detect_ats_platform(page) == ATSPlatform.BAMBOOHR

    page.url = "https://jobs.smartrecruiters.com/Acme/123"
    assert automation.detect_ats_platform(page) == ATSPlatform.SMARTRECRUITERS

    page.url = "https://careers.google.com/jobs"
    assert automation.detect_ats_platform(page) == ATSPlatform.CUSTOM


@pytest.mark.asyncio
async def test_human_type(automation):
    page = AsyncMock(spec=Page)
    page.keyboard.type = AsyncMock()
    element = AsyncMock()
    page.wait_for_selector.return_value = element

    await automation.human_type(page, "#name", "John")

    page.wait_for_selector.assert_called_with("#name", state="visible", timeout=10000)
    element.click.assert_called_once()
    assert page.keyboard.type.call_count == 4  # 4 chars in "John"


@pytest.mark.asyncio
async def test_human_scroll(automation):
    page = AsyncMock(spec=Page)
    page.mouse.wheel = AsyncMock()
    page.evaluate.side_effect = [
        2000,  # Total height
        800,  # Viewport
        2000,  # Height again (loop check)
        2000,
        2000,
        2000,
    ]

    # We patch sleep to make test fast
    with patch("asyncio.sleep", new_callable=AsyncMock):
        await automation.human_scroll(page)

    # Verify mouse wheel usage
    assert page.mouse.wheel.called


@pytest.mark.asyncio
async def test_close_cleanup(automation, mock_playwright):
    # Initialize
    await automation.navigate_to_job("https://example.com")

    await automation.close()

    # Verify everything closed
    playwright_obj = mock_playwright.return_value.start.return_value
    browser_obj = playwright_obj.chromium.launch.return_value
    context_obj = browser_obj.new_context.return_value

    context_obj.close.assert_called_once()
    browser_obj.close.assert_called_once()
    playwright_obj.stop.assert_called()
