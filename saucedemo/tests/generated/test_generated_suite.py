import re
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "https://www.saucedemo.com"


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Login as standard_user and return the page."""
    page.goto(BASE_URL)
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("#login-button").click()
    page.wait_for_url("**/inventory.html")
    return page


class TestSauceDemoSuite:
    """Generated test suite for SauceDemo."""

    def test_successful_login(self, page: Page):
        """Test successful login with valid credentials."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        expect(page).to_have_url(re.compile(r".*/inventory\.html"))
        expect(page.locator(".inventory_list")).to_be_visible()

    def test_failed_login(self, page: Page):
        """Test login failure with invalid credentials."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("invalid_user")
        page.locator("#password").fill("wrong_password")
        page.locator("#login-button").click()
        expect(page.locator('[data-test="error"]')).to_be_visible()

    def test_locked_out_user(self, page: Page):
        """Test locked out user cannot login."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("locked_out_user")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        error = page.locator('[data-test="error"]')
        expect(error).to_be_visible()
        expect(error).to_contain_text("locked out")

    def test_add_single_item_to_cart(self, logged_in_page: Page):
        """Test adding a single item to cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
        page.locator(".shopping_cart_link").click()
        expect(page).to_have_url(re.compile(r".*/cart\.html"))
        expect(page.locator(".cart_item")).to_have_count(1)
        expect(page.locator(".cart_item")).to_contain_text("Sauce Labs Backpack")

    def test_add_multiple_items_to_cart(self, logged_in_page: Page):
        """Test adding multiple items to cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        page.locator(".shopping_cart_link").click()
        expect(page).to_have_url(re.compile(r".*/cart\.html"))
        cart_items = page.locator(".cart_item")
        expect(cart_items).to_have_count(2)
        expect(cart_items.nth(0)).to_contain_text("Sauce Labs Backpack")
        expect(cart_items.nth(1)).to_contain_text("Sauce Labs Bike Light")

    def test_remove_item_from_cart(self, logged_in_page: Page):
        """Test removing an item from cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
        page.locator(".shopping_cart_link").click()
        expect(page.locator(".cart_item")).to_have_count(1)
        page.locator('[data-test^="remove-"]').click()
        expect(page.locator(".cart_item")).to_have_count(0)
        expect(page.locator(".shopping_cart_badge")).not_to_be_visible()

    def test_complete_checkout(self, logged_in_page: Page):
        """Test complete checkout flow."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator(".shopping_cart_link").click()
        page.locator('[data-test="checkout"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-step-one\.html"))
        page.locator('[data-test="firstName"]').fill("John")
        page.locator('[data-test="lastName"]').fill("Doe")
        page.locator('[data-test="postalCode"]').fill("12345")
        page.locator('[data-test="continue"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-step-two\.html"))
        expect(page.locator(".cart_list")).to_be_visible()
        page.locator('[data-test="finish"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-complete\.html"))
        expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")

    def test_logout(self, logged_in_page: Page):
        """Test user logout."""
        page = logged_in_page
        page.locator("#react-burger-menu-btn").click()
        page.locator("#logout_sidebar_link").click()
        expect(page).to_have_url(BASE_URL + "/")

    def test_failed_login_empty_username(self, page: Page):
        """Test login failure with empty username."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("")
        page.locator("#password").fill("secret_sauce")
        page.locator("#login-button").click()
        expect(page.locator('[data-test="error"]')).to_be_visible()

    def test_failed_login_empty_password(self, page: Page):
        """Test login failure with empty password."""
        page.goto(BASE_URL)
        page.locator("#user-name").fill("standard_user")
        page.locator("#password").fill("")
        page.locator("#login-button").click()
        expect(page.locator('[data-test="error"]')).to_be_visible()

    def test_add_and_remove_multiple_items(self, logged_in_page: Page):
        """Add multiple items and remove one from cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator('[data-test="add-to-cart-sauce-labs-bike-light"]').click()
        expect(page.locator(".shopping_cart_badge")).to_have_text("2")
        page.locator(".shopping_cart_link").click()
        expect(page.locator(".cart_item")).to_have_count(2)
        # Remove one item
        page.locator('[data-test="remove-sauce-labs-backpack"]').click()
        expect(page.locator(".cart_item")).to_have_count(1)
        expect(page.locator(".shopping_cart_badge")).to_have_text("1")
        expect(page.locator(".cart_item")).to_contain_text("Sauce Labs Bike Light")

    def test_checkout_cancel_on_step_one(self, logged_in_page: Page):
        """Test cancel button on checkout step one returns to cart."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator(".shopping_cart_link").click()
        page.locator('[data-test="checkout"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-step-one\.html"))
        page.locator('[data-test="cancel"]').click()
        expect(page).to_have_url(re.compile(r".*/cart\.html"))

    def test_checkout_cancel_on_step_two(self, logged_in_page: Page):
        """Test cancel button on checkout step two returns to checkout step one."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator(".shopping_cart_link").click()
        page.locator('[data-test="checkout"]').click()
        page.locator('[data-test="firstName"]').fill("Jane")
        page.locator('[data-test="lastName"]').fill("Smith")
        page.locator('[data-test="postalCode"]').fill("54321")
        page.locator('[data-test="continue"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-step-two\.html"))
        page.locator('[data-test="cancel"]').click()
        expect(page).to_have_url(re.compile(r".*/checkout-step-one\.html"))

    def test_checkout_error_missing_info(self, logged_in_page: Page):
        """Test error message when checkout info is incomplete."""
        page = logged_in_page
        page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
        page.locator(".shopping_cart_link").click()
        page.locator('[data-test="checkout"]').click()
        page.locator('[data-test="firstName"]').fill("")
        page.locator('[data-test="lastName"]').fill("")
        page.locator('[data-test="postalCode"]').fill("")
        page.locator('[data-test="continue"]').click()
        error = page.locator('[data-test="error"]')
        expect(error).to_be_visible()
        expect(error).to_contain_text("Error")

    def test_inventory_sort_dropdown_visible(self, logged_in_page: Page):
        """Test that the product sort dropdown is visible on inventory page."""
        page = logged_in_page
        expect(page.locator('[data-test="product-sort-container"]')).to_be_visible()

    def test_cart_badge_not_visible_when_empty(self, logged_in_page: Page):
        """Test that cart badge is not visible when no items added."""
        page = logged_in_page
        expect(page.locator(".shopping_cart_badge")).not_to_be_visible()