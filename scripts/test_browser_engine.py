import asyncio
import logging
import base64
from src.agent.browser.pool import BrowserPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def verify_browser_engine():
    pool = BrowserPool()
    try:
        logger.info("1. Initializing Browser Pool...")
        await pool.initialize()

        logger.info("2. Acquiring Browser for user 'test_user'...")
        browser = await pool.acquire_browser("test_user")

        url = "https://example.com"
        logger.info(f"3. Navigating to {url}...")
        await browser.navigate(url)

        logger.info("4. Testing DOM Capture...")
        dom = await browser.get_dom_snapshot()
        logger.info(f"DOM Title captured: {dom.get('title')}")
        assert "Example Domain" in dom.get("title")

        logger.info("5. Testing Screenshot...")
        screenshot_b64 = await browser.take_screenshot()
        assert len(screenshot_b64) > 100
        logger.info(
            "Screenshot captured successfully (base64 length: %d)", len(screenshot_b64)
        )

        logger.info("6. Testing Stealth Check (navigator.webdriver)...")
        is_webdriver = await browser.page.evaluate("navigator.webdriver")
        logger.info(
            f"navigator.webdriver = {is_webdriver} (Should be undefined or false)"
        )
        assert not is_webdriver

        logger.info("7. Releasing Browser...")
        await pool.release_browser(browser)

        logger.info("BROWSER ENGINE VERIFICATION PASSED ✅")

    except Exception as e:
        logger.error(f"Verification FAILED: {e}")
        raise
    finally:
        await pool.shutdown()


if __name__ == "__main__":
    asyncio.run(verify_browser_engine())
