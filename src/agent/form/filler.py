from typing import Any, Dict, List

import structlog
from pydantic import BaseModel

from playwright.async_api import Page
from src.agent.browser.stealth import StealthBrowser
from src.agent.form.mapper import FieldMapping

logger = structlog.get_logger(__name__)


class FormFillResult(BaseModel):
    filled: List[str]
    failed: List[Dict[str, str]]
    skipped: List[str]


class FormFiller:
    """
    Executes the filling of forms based on a mapping using stealth interactions.
    """

    def __init__(self, stealth_browser: StealthBrowser):
        self.stealth = stealth_browser

    async def fill_form(
        self, page: Page, mappings: List[FieldMapping]
    ) -> FormFillResult:
        """
        Fill all mapped fields with human-like behavior.
        """
        results = {"filled": [], "failed": [], "skipped": []}

        for mapping in mappings:
            try:
                if mapping.value is None:
                    results["skipped"].append(mapping.selector)
                    continue

                # Locate element
                element = page.locator(mapping.selector).first
                if not await element.count():
                    logger.warning(
                        "Field not found during fill", selector=mapping.selector
                    )
                    results["failed"].append(
                        {"selector": mapping.selector, "error": "Element not found"}
                    )
                    continue

                # Determine interaction type based on tag and type
                # We start with evaluation to avoid multiple wire calls
                tag_info = await element.evaluate("""el => {
                    return {
                        tagName: el.tagName.toLowerCase(),
                        type: el.type || '',
                        isChecked: el.checked || false
                    }
                }""")

                tag = tag_info["tagName"]
                input_type = tag_info["type"].lower()

                if tag == "select":
                    # Handle Select
                    await self._fill_select(page, mapping)

                elif tag == "textarea":
                    # Handle Textarea
                    await self._fill_text(page, mapping, element, is_textarea=True)

                elif tag == "input":
                    if input_type == "checkbox":
                        # Handle Checkbox
                        await self._fill_checkbox(
                            page, mapping, element, tag_info["isChecked"]
                        )

                    elif input_type == "radio":
                        # Handle Radio - assume value implies we should click it
                        # For radios, the selector usually points to the specific option
                        await self.stealth.human_click(page, mapping.selector)

                    elif input_type == "file":
                        # Handle File Upload
                        await self._fill_file(page, mapping, element)

                    elif input_type in ["submit", "button", "image", "reset", "hidden"]:
                        # Skip non-fillable inputs
                        results["skipped"].append(mapping.selector)
                        continue

                    else:
                        # Handle standard input (text, email, tel, date, number, etc.)
                        await self._fill_text(page, mapping, element)

                results["filled"].append(mapping.selector)

                # Human-like delay between fields
                await self.stealth.random_delay(300, 800)

            except Exception as e:
                logger.warning(
                    "Failed to fill field", selector=mapping.selector, error=str(e)
                )
                results["failed"].append(
                    {"selector": mapping.selector, "error": str(e)}
                )

        return FormFillResult(**results)

    async def _fill_select(self, page: Page, mapping: FieldMapping):
        """Handle select dropdowns."""
        # mapping.value should be the option 'value'.
        # We can also verify if it matches text if value fails?
        # Playwright select_option can take value, label, or index.
        val = str(mapping.value)
        await page.select_option(mapping.selector, value=val)

    async def _fill_text(
        self, page: Page, mapping: FieldMapping, element, is_textarea=False
    ):
        """Handle text inputs and textareas."""
        await element.click()
        await element.fill("")  # Clear first

        # Use stealth typing
        speed = "fast" if is_textarea and len(str(mapping.value)) > 100 else "normal"
        await self.stealth.human_type(
            page, mapping.selector, str(mapping.value), speed=speed
        )

    async def _fill_checkbox(
        self, page: Page, mapping: FieldMapping, element, current_checked: bool
    ):
        """Handle checkboxes."""
        val = str(mapping.value).lower()
        should_check = val in ("true", "yes", "1", "on")

        if current_checked != should_check:
            await self.stealth.human_click(page, mapping.selector)

    async def _fill_file(self, page: Page, mapping: FieldMapping, element):
        """Handle file uploads."""
        file_path = str(mapping.value)

        # Playwright file chooser handling
        async with page.expect_file_chooser() as fc_info:
            # Some file inputs are hidden and open via a label click.
            # If element is visible, click it. If hidden, we might need to click its label?
            # Or use set_input_files direct on input if possible.
            if await element.is_visible():
                await element.click()
            else:
                # If hidden, try set_input_files directly which bypasses chooser dialog need usually
                # But to simulate user we want chooser.
                # However, set_input_files works on hidden inputs too often.
                await element.set_input_files(file_path)
                return

        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)
