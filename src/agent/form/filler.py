from typing import Any, Dict

from src.agent.browser.engine import BrowserEngine


class FormFiller:
    """
    Executes the filling of forms based on a mapping.
    """

    def __init__(self, browser: BrowserEngine):
        self.browser = browser

    async def fill(self, mapping: Dict[str, Any]):
        """
        Fills the form fields.
        """
        for selector, value in mapping.items():
            if value is None:
                continue

            # Check if it's a select or input
            # Simple heuristic: try fill, if fail try select_option
            # Better: pass field type in mapping

            try:
                # We simply try to fill for now.
                # Playwright's fill works for <input> and <textarea>.
                # For <select>, we need select_option.
                # We can try to guess or use a specific method if we had the type.

                # Robust approach: check element type
                element_type = await self.browser.page.evaluate(
                    f"el => el.tagName",
                    await self.browser.page.query_selector(selector),
                )

                if element_type == "SELECT":
                    await self.browser.page.select_option(
                        selector, value=str(value)
                    )  # value or label?
                elif element_type == "INPUT":
                    # Check for checkbox/radio
                    type_attr = await self.browser.page.get_attribute(selector, "type")
                    if type_attr in ["checkbox", "radio"]:
                        if value:
                            await self.browser.page.check(selector)
                        else:
                            await self.browser.page.uncheck(selector)
                    else:
                        await self.browser.page.fill(selector, str(value))
                else:
                    await self.browser.page.fill(selector, str(value))

            except Exception as e:
                # Log warning but continue filling other fields
                print(f"Failed to fill {selector} with {value}: {e}")
