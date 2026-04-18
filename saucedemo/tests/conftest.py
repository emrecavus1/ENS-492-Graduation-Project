"""
Pytest configuration for SauceDemo Playwright tests.
"""
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


BASE_URL = "https://www.saucedemo.com"


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    """Create a new browser context for each test."""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def base_url() -> str:
    """Return the base URL for SauceDemo."""
    return BASE_URL


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Login as standard_user and return the page."""
    page.goto(BASE_URL)
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("#login-button").click()
    page.wait_for_url("**/inventory.html")
    return page
