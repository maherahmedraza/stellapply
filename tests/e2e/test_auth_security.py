import pytest
from playwright.sync_api import Page, expect
import time


def test_auth_security_flow(page: Page):
    # Timestamp to ensure unique email
    timestamp = int(time.time())
    email = f"security_test_{timestamp}@example.com"
    password = "StrongPassword123!"

    # 1. Registration
    page.goto("http://localhost:3000/register")
    expect(page).to_have_title(r"StellarApply")  # Adjust if title differs

    # Fill Registration Form
    page.get_by_label("Full Name").fill("Security Tester")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    # Assuming there's a confirm password or just submit
    # page.get_by_label("Confirm Password").fill(password)
    page.get_by_role("button", name="Create Account").click()

    # Verify success (redirect or message)
    # Expect redirect to dashboard or login
    # Let's assume auto-login to dashboard, or redirect to login.
    # Adjust based on actual flow.
    # If it goes to login:
    # expect(page).to_have_url(r".*/login")

    # If it goes to dashboard directly:
    expect(page).to_have_url(r".*/dashboard", timeout=10000)

    # 2. Logout
    page.get_by_role("button", name="User menu").click()  # Adjust selector
    page.get_by_role("menuitem", name="Log out").click()
    expect(page).to_have_url(r".*/login")

    # 3. Security Check: Invalid Password
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill("WrongPassword!")
    page.get_by_role("button", name="Sign In").click()

    # Expect error message
    expect(page.get_by_text("Invalid credentials")).to_be_visible()

    # 4. Success Login
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign In").click()
    expect(page).to_have_url(r".*/dashboard")

    # 5. Check Token Storage (Security)
    # Verify access_token is in localStorage or cookies
    # This might depend on implementation (httpOnly cookie vs localStorage)
    # If localStorage:
    # token = page.evaluate("localStorage.getItem('access_token')")
    # assert token is not None
