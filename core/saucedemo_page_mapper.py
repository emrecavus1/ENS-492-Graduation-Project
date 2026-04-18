"""
SauceDemo Page Mapper Module

Maps UI pages and user flows for the SauceDemo application.
Equivalent to route_mapper.py but for UI-based E2E testing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PageInfo:
    """Represents a UI page in SauceDemo."""
    name: str
    url_pattern: str
    description: str = ""
    requires_auth: bool = False
    selectors: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_public(self) -> bool:
        return not self.requires_auth


@dataclass
class UserFlow:
    """Represents a user flow/scenario in SauceDemo."""
    name: str
    description: str
    pages_involved: List[str]
    steps: List[str]
    priority: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW


SAUCEDEMO_PAGES: Dict[str, PageInfo] = {
    "login": PageInfo(
        name="login",
        url_pattern="/",
        description="Login page with username/password form",
        requires_auth=False,
        selectors={
            "username": "#user-name",
            "password": "#password",
            "login_button": "#login-button",
            "error_message": '[data-test="error"]',
        },
    ),
    "inventory": PageInfo(
        name="inventory",
        url_pattern="/inventory.html",
        description="Product listing page showing all items",
        requires_auth=True,
        selectors={
            "inventory_list": ".inventory_list",
            "inventory_item": ".inventory_item",
            "add_to_cart_backpack": '[data-test="add-to-cart-sauce-labs-backpack"]',
            "add_to_cart_bike_light": '[data-test="add-to-cart-sauce-labs-bike-light"]',
            "sort_dropdown": '[data-test="product-sort-container"]',
            "cart_badge": ".shopping_cart_badge",
            "cart_link": ".shopping_cart_link",
            "burger_menu": "#react-burger-menu-btn",
        },
    ),
    "inventory_item": PageInfo(
        name="inventory_item",
        url_pattern="/inventory-item.html",
        description="Individual product detail page",
        requires_auth=True,
        selectors={
            "item_name": ".inventory_details_name",
            "item_price": ".inventory_details_price",
            "item_desc": ".inventory_details_desc",
            "add_to_cart": '[data-test^="add-to-cart"]',
            "back_button": '[data-test="back-to-products"]',
        },
    ),
    "cart": PageInfo(
        name="cart",
        url_pattern="/cart.html",
        description="Shopping cart page",
        requires_auth=True,
        selectors={
            "cart_list": ".cart_list",
            "cart_item": ".cart_item",
            "checkout_button": '[data-test="checkout"]',
            "continue_shopping": '[data-test="continue-shopping"]',
            "remove_item": '[data-test^="remove-"]',
        },
    ),
    "checkout_step_one": PageInfo(
        name="checkout_step_one",
        url_pattern="/checkout-step-one.html",
        description="Checkout form - customer information",
        requires_auth=True,
        selectors={
            "first_name": '[data-test="firstName"]',
            "last_name": '[data-test="lastName"]',
            "postal_code": '[data-test="postalCode"]',
            "continue_button": '[data-test="continue"]',
            "cancel_button": '[data-test="cancel"]',
            "error_message": '[data-test="error"]',
        },
    ),
    "checkout_step_two": PageInfo(
        name="checkout_step_two",
        url_pattern="/checkout-step-two.html",
        description="Checkout overview - order summary",
        requires_auth=True,
        selectors={
            "cart_list": ".cart_list",
            "summary_subtotal": ".summary_subtotal_label",
            "summary_tax": ".summary_tax_label",
            "summary_total": ".summary_total_label",
            "finish_button": '[data-test="finish"]',
            "cancel_button": '[data-test="cancel"]',
        },
    ),
    "checkout_complete": PageInfo(
        name="checkout_complete",
        url_pattern="/checkout-complete.html",
        description="Order confirmation page",
        requires_auth=True,
        selectors={
            "complete_header": ".complete-header",
            "complete_text": ".complete-text",
            "back_home_button": '[data-test="back-to-products"]',
        },
    ),
}


SAUCEDEMO_FLOWS: List[UserFlow] = [
    UserFlow(
        name="successful_login",
        description="User logs in with valid credentials",
        pages_involved=["login", "inventory"],
        steps=[
            "Navigate to login page",
            "Enter valid username (standard_user)",
            "Enter valid password (secret_sauce)",
            "Click login button",
            "Verify redirect to inventory page",
        ],
        priority="CRITICAL",
    ),
    UserFlow(
        name="failed_login",
        description="User attempts login with invalid credentials",
        pages_involved=["login"],
        steps=[
            "Navigate to login page",
            "Enter invalid username",
            "Enter invalid password",
            "Click login button",
            "Verify error message is displayed",
        ],
        priority="CRITICAL",
    ),
    UserFlow(
        name="locked_out_user",
        description="Locked out user cannot login",
        pages_involved=["login"],
        steps=[
            "Navigate to login page",
            "Enter locked_out_user as username",
            "Enter secret_sauce as password",
            "Click login button",
            "Verify locked out error message",
        ],
        priority="HIGH",
    ),
    UserFlow(
        name="add_single_item_to_cart",
        description="Add one item to cart from inventory",
        pages_involved=["login", "inventory", "cart"],
        steps=[
            "Login as standard_user",
            "Click add to cart on any item",
            "Verify cart badge shows 1",
            "Click cart icon",
            "Verify item appears in cart",
        ],
        priority="CRITICAL",
    ),
    UserFlow(
        name="add_multiple_items_to_cart",
        description="Add multiple items to cart",
        pages_involved=["login", "inventory", "cart"],
        steps=[
            "Login as standard_user",
            "Add Sauce Labs Backpack to cart",
            "Add Sauce Labs Bike Light to cart",
            "Verify cart badge shows 2",
            "Navigate to cart",
            "Verify both items appear",
        ],
        priority="HIGH",
    ),
    UserFlow(
        name="remove_item_from_cart",
        description="Remove item from cart",
        pages_involved=["login", "inventory", "cart"],
        steps=[
            "Login and add item to cart",
            "Navigate to cart",
            "Click remove button",
            "Verify item is removed",
            "Verify cart badge updates",
        ],
        priority="HIGH",
    ),
    UserFlow(
        name="complete_checkout",
        description="Complete full checkout flow",
        pages_involved=["login", "inventory", "cart", "checkout_step_one", "checkout_step_two", "checkout_complete"],
        steps=[
            "Login as standard_user",
            "Add item to cart",
            "Navigate to cart",
            "Click checkout",
            "Fill in customer info (first name, last name, postal code)",
            "Click continue",
            "Verify order summary",
            "Click finish",
            "Verify order complete message",
        ],
        priority="CRITICAL",
    ),
    UserFlow(
        name="checkout_validation",
        description="Checkout form validation",
        pages_involved=["login", "inventory", "cart", "checkout_step_one"],
        steps=[
            "Login and add item to cart",
            "Navigate to checkout",
            "Try to continue without filling form",
            "Verify error message for missing first name",
            "Fill first name, try again",
            "Verify error for missing last name",
        ],
        priority="MEDIUM",
    ),
    UserFlow(
        name="sort_products",
        description="Sort products by different criteria",
        pages_involved=["login", "inventory"],
        steps=[
            "Login as standard_user",
            "Select 'Price (low to high)' from sort dropdown",
            "Verify products are sorted by price ascending",
            "Select 'Price (high to low)'",
            "Verify products are sorted by price descending",
            "Select 'Name (Z to A)'",
            "Verify products are sorted alphabetically descending",
        ],
        priority="MEDIUM",
    ),
    UserFlow(
        name="view_product_details",
        description="View individual product details",
        pages_involved=["login", "inventory", "inventory_item"],
        steps=[
            "Login as standard_user",
            "Click on product name or image",
            "Verify product detail page loads",
            "Verify product name, price, description visible",
            "Click back to products",
            "Verify return to inventory",
        ],
        priority="MEDIUM",
    ),
    UserFlow(
        name="burger_menu_navigation",
        description="Use burger menu for navigation",
        pages_involved=["login", "inventory"],
        steps=[
            "Login as standard_user",
            "Click burger menu icon",
            "Verify menu opens",
            "Click 'About' link",
            "Verify navigation to saucelabs.com",
        ],
        priority="LOW",
    ),
    UserFlow(
        name="logout",
        description="User logs out successfully",
        pages_involved=["login", "inventory"],
        steps=[
            "Login as standard_user",
            "Click burger menu",
            "Click logout",
            "Verify redirect to login page",
        ],
        priority="HIGH",
    ),
    UserFlow(
        name="problem_user_experience",
        description="Test with problem_user account",
        pages_involved=["login", "inventory"],
        steps=[
            "Login as problem_user",
            "Observe broken images",
            "Try to add items to cart",
            "Verify unexpected behavior",
        ],
        priority="LOW",
    ),
    UserFlow(
        name="performance_glitch_user",
        description="Test with performance_glitch_user",
        pages_involved=["login", "inventory"],
        steps=[
            "Login as performance_glitch_user",
            "Observe slow page loads",
            "Verify eventual page functionality",
        ],
        priority="LOW",
    ),
]


def get_all_pages() -> Dict[str, PageInfo]:
    """Return all SauceDemo pages."""
    return SAUCEDEMO_PAGES


def get_all_flows() -> List[UserFlow]:
    """Return all user flows."""
    return SAUCEDEMO_FLOWS


def get_flows_by_priority(priorities: List[str]) -> List[UserFlow]:
    """Get flows filtered by priority levels."""
    return [f for f in SAUCEDEMO_FLOWS if f.priority in priorities]


def get_flows_for_pages(page_names: List[str]) -> List[UserFlow]:
    """Get flows that involve specific pages."""
    return [
        f for f in SAUCEDEMO_FLOWS
        if any(p in f.pages_involved for p in page_names)
    ]


def get_uncovered_flows(covered_pages: List[str]) -> List[UserFlow]:
    """Get flows that have pages not yet covered."""
    return [
        f for f in SAUCEDEMO_FLOWS
        if not all(p in covered_pages for p in f.pages_involved)
    ]
