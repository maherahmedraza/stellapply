from typing import List

from playwright.async_api import Page
from pydantic import BaseModel


class FormField(BaseModel):
    name: str | None
    id: str | None
    type: str  # text, password, email, checkbox, select, etc.
    label: str | None
    selector: str
    required: bool = False


class FormDetector:
    """
    Analyzes a page to identify form fields.
    """

    async def detect_fields(self, page: Page) -> List[FormField]:
        """
        Scan the page for inputs, selects, and textareas.
        """
        # This is a simplified detection logic.
        # A robust version would use evaluate() to run JS in the browser context
        # to properly associate labels with inputs (for attributes, aria-labels, closest text).

        fields = []

        # Detect standard inputs
        inputs = await page.locator("input, select, textarea").all()

        for i, element in enumerate(inputs):
            # We need to execute JS to get attributes efficiently
            # For this MVP, we'll try to get basic attributes if possible
            # But iterating locators in Python is slow.
            # Better to use page.evaluate() to get all data at once.
            pass

        # Optimized approach using JS execution
        field_data = await page.evaluate("""() => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            return inputs.map(el => {
                let labelText = null;
                if (el.id) {
                    const label = document.querySelector(`label[for="${el.id}"]`);
                    if (label) labelText = label.innerText;
                }
                if (!labelText && el.closest('label')) {
                    labelText = el.closest('label').innerText;
                }
                
                return {
                    name: el.name || null,
                    id: el.id || null,
                    type: el.type || el.tagName.toLowerCase(),
                    label: labelText || el.placeholder || el.getAttribute('aria-label') || null,
                    required: el.required || false,
                    // We generate a unique selector logic here or assume basic tag logic
                    // For simplicity in Python we might rely on ID or Name if available
                };
            });
        }""")

        for data in field_data:
            # Construct a simple selector
            selector = ""
            if data["id"]:
                selector = f"#{CSS.escape(data['id'])}"
            elif data["name"]:
                selector = f"[name='{data['name']}']"
            else:
                # Fallback, tricky without unique path.
                # For now skip if no ID or Name
                continue

            fields.append(
                FormField(
                    name=data["name"],
                    id=data["id"],
                    type=data["type"],
                    label=data["label"],
                    selector=selector,
                    required=data["required"],
                )
            )

        return fields
