import pytest
from playwright.sync_api import Page, expect


def test_login_flow(page: Page):
    # 1. Navigate to Home
    page.goto("http://localhost:3000")
    expect(page).to_have_title(r"StellarApply")

    # 2. Check for Login/Register button (assuming "Get Started" or "Login")
    # Adjust selectors based on actual UI (Shadcn often uses specific classes)
    # searching for text "Login" or "Sign In"
    login_link = page.get_by_role("link", name="Login")
    if login_link.count() > 0:
        login_link.click()
    else:
        # Maybe "Get Started" triggers login?
        page.get_by_role("link", name="Get Started").click()

    # 3. Fill Login Forms
    # Assuming /login page
    expect(page).to_have_url(r".*/login")

    page.get_by_label("Email").fill("test@example.com")
    page.get_by_label("Password").fill("Password123!")
    page.get_by_role("button", name="Sign In").click()

    # 4. Verify Redirect to Dashboard
    # Expect URL to contain /dashboard
    expect(page).to_have_url(r".*/dashboard")
    expect(page.get_by_role("heading", name="Welcome")).to_be_visible()
