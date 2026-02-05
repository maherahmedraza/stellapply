from typing import List, Dict, Any, Optional

from playwright.async_api import Page
from pydantic import BaseModel, Field


class FormField(BaseModel):
    name: str | None
    id: str | None
    type: str  # text, password, email, checkbox, select, etc.
    label: str | None
    selector: str
    required: bool = False
    placeholder: str | None = None
    options: List[Dict[str, str]] = Field(
        default_factory=list
    )  # For select: [{text: "USA", value: "US"}]


class FormDetector:
    """
    Analyzes a page to identify form fields.
    """

    async def detect_fields(self, page: Page) -> List[FormField]:
        """
        Scan the page for inputs, selects, and textareas.
        """
        # Optimized approach using JS execution to get deep details
        field_data = await page.evaluate("""() => {
            const inputs = Array.from(document.querySelectorAll('input, select, textarea'));
            
            return inputs.map(el => {
                let labelText = null;
                
                // Strategy 1: Explicit label with 'for'
                if (el.id) {
                    const label = document.querySelector(`label[for="${el.id}"]`);
                    if (label) labelText = label.innerText;
                }
                
                // Strategy 2: Nested inside label
                if (!labelText && el.closest('label')) {
                    const clone = el.closest('label').cloneNode(true);
                    // Remove the input itself from clone to get just text
                    const inputInClone = clone.querySelector('input, select, textarea');
                    if (inputInClone) inputInClone.remove();
                    labelText = clone.innerText;
                }
                
                // Strategy 3: Aria-label
                if (!labelText) {
                    labelText = el.getAttribute('aria-label');
                }

                // Clean label
                if (labelText) labelText = labelText.trim();

                // Get options for select
                let options = [];
                if (el.tagName === 'SELECT') {
                    options = Array.from(el.options).map(opt => ({
                        text: opt.innerText.trim(),
                        value: opt.value
                    }));
                }

                return {
                    name: el.name || null,
                    id: el.id || null,
                    type: el.type || el.tagName.toLowerCase(),
                    label: labelText,
                    placeholder: el.placeholder || null,
                    required: el.required || false,
                    options: options
                };
            });
        }""")

        fields = []
        for data in field_data:
            # Construct a safe simple selector
            selector = ""
            if data["id"]:
                selector = f"#{CSS.escape(data['id'])}"
            elif data["name"]:
                selector = f"[name='{data['name']}']"
            else:
                # Fallback: try to construct a unique selector if possible
                # This logic is fragile without unique ID/Name.
                # Ideally we'd get a full path from JS, but for now we skip tricky ones.
                continue

            fields.append(
                FormField(
                    name=data["name"],
                    id=data["id"],
                    type=data["type"],
                    label=data["label"],
                    selector=selector,
                    required=data["required"],
                    placeholder=data["placeholder"],
                    options=data["options"],
                )
            )

        return fields
