"""
Spree Route Mapper Module

Maps Spree Commerce Store API v3 endpoints for test generation.
Based on Spree's OpenAPI specification at /api/v3/store/
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SpreeEndpointInfo:
    """Represents a Spree API endpoint."""
    method: str
    path: str
    description: str = ""
    requires_auth: bool = False
    request_body: Optional[str] = None
    safe_for_coverage: bool = True
    resource: str = ""
    
    @property
    def is_get(self) -> bool:
        return self.method == "GET"
    
    @property
    def is_read_only(self) -> bool:
        return self.method in ("GET", "HEAD", "OPTIONS")


@dataclass
class SpreeResourceInfo:
    """Represents a Spree API resource/controller."""
    name: str
    base_path: str
    description: str = ""
    endpoints: List[SpreeEndpointInfo] = None
    
    def __post_init__(self):
        if self.endpoints is None:
            self.endpoints = []


SPREE_STORE_API_RESOURCES: Dict[str, SpreeResourceInfo] = {
    "products": SpreeResourceInfo(
        name="products",
        base_path="/api/v3/store/products",
        description="Product catalog endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/products", "List all products", resource="products"),
            SpreeEndpointInfo("GET", "/api/v3/store/products/:id", "Get product details", resource="products"),
        ],
    ),
    
    "taxons": SpreeResourceInfo(
        name="taxons",
        base_path="/api/v3/store/taxons",
        description="Category/taxonomy endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/taxons", "List all taxons/categories", resource="taxons"),
            SpreeEndpointInfo("GET", "/api/v3/store/taxons/:id", "Get taxon details", resource="taxons"),
        ],
    ),
    
    "cart": SpreeResourceInfo(
        name="cart",
        base_path="/api/v3/store/cart",
        description="Shopping cart endpoints",
        endpoints=[
            SpreeEndpointInfo("POST", "/api/v3/store/cart", "Create a new cart", resource="cart"),
            SpreeEndpointInfo("GET", "/api/v3/store/cart", "Get current cart", requires_auth=True, resource="cart"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/cart", "Update cart", requires_auth=True, resource="cart"),
            SpreeEndpointInfo("DELETE", "/api/v3/store/cart", "Clear cart", requires_auth=True, safe_for_coverage=False, resource="cart"),
            SpreeEndpointInfo("POST", "/api/v3/store/cart/add_item", "Add item to cart", requires_auth=True, resource="cart"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/cart/set_quantity", "Set item quantity", requires_auth=True, resource="cart"),
            SpreeEndpointInfo("DELETE", "/api/v3/store/cart/remove_line_item/:id", "Remove item from cart", requires_auth=True, safe_for_coverage=False, resource="cart"),
            SpreeEndpointInfo("POST", "/api/v3/store/cart/apply_coupon_code", "Apply coupon code", requires_auth=True, resource="cart"),
        ],
    ),
    
    "checkout": SpreeResourceInfo(
        name="checkout",
        base_path="/api/v3/store/checkout",
        description="Checkout flow endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/checkout", "Get checkout state", requires_auth=True, resource="checkout"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/checkout", "Update checkout", requires_auth=True, resource="checkout"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/checkout/next", "Advance checkout state", requires_auth=True, resource="checkout"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/checkout/advance", "Advance to furthest state", requires_auth=True, resource="checkout"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/checkout/complete", "Complete checkout", requires_auth=True, safe_for_coverage=False, resource="checkout"),
        ],
    ),
    
    "account": SpreeResourceInfo(
        name="account",
        base_path="/api/v3/store/account",
        description="User account endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/account", "Get current user account", requires_auth=True, resource="account"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/account", "Update account", requires_auth=True, resource="account"),
            SpreeEndpointInfo("POST", "/api/v3/store/account", "Create account (register)", resource="account"),
        ],
    ),
    
    "account_orders": SpreeResourceInfo(
        name="account_orders",
        base_path="/api/v3/store/account/orders",
        description="User order history endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/account/orders", "List user orders", requires_auth=True, resource="account_orders"),
            SpreeEndpointInfo("GET", "/api/v3/store/account/orders/:id", "Get order details", requires_auth=True, resource="account_orders"),
        ],
    ),
    
    "account_addresses": SpreeResourceInfo(
        name="account_addresses",
        base_path="/api/v3/store/account/addresses",
        description="User address book endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/account/addresses", "List user addresses", requires_auth=True, resource="account_addresses"),
            SpreeEndpointInfo("POST", "/api/v3/store/account/addresses", "Create address", requires_auth=True, resource="account_addresses"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/account/addresses/:id", "Update address", requires_auth=True, resource="account_addresses"),
            SpreeEndpointInfo("DELETE", "/api/v3/store/account/addresses/:id", "Delete address", requires_auth=True, safe_for_coverage=False, resource="account_addresses"),
        ],
    ),
    
    "account_credit_cards": SpreeResourceInfo(
        name="account_credit_cards",
        base_path="/api/v3/store/account/credit_cards",
        description="Saved payment methods",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/account/credit_cards", "List saved cards", requires_auth=True, resource="account_credit_cards"),
        ],
    ),
    
    "countries": SpreeResourceInfo(
        name="countries",
        base_path="/api/v3/store/countries",
        description="Country data endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/countries", "List all countries", resource="countries"),
            SpreeEndpointInfo("GET", "/api/v3/store/countries/:iso", "Get country by ISO code", resource="countries"),
            SpreeEndpointInfo("GET", "/api/v3/store/countries/default", "Get default country", resource="countries"),
        ],
    ),
    
    "states": SpreeResourceInfo(
        name="states",
        base_path="/api/v3/store/states",
        description="State/province data endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/states", "List all states", resource="states"),
        ],
    ),
    
    "stores": SpreeResourceInfo(
        name="stores",
        base_path="/api/v3/store/store",
        description="Store information endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/store", "Get current store info", resource="stores"),
        ],
    ),
    
    "menus": SpreeResourceInfo(
        name="menus",
        base_path="/api/v3/store/menus",
        description="Navigation menu endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/menus", "List all menus", resource="menus"),
            SpreeEndpointInfo("GET", "/api/v3/store/menus/:id", "Get menu details", resource="menus"),
        ],
    ),
    
    "pages": SpreeResourceInfo(
        name="pages",
        base_path="/api/v3/store/pages",
        description="CMS pages endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/pages", "List all pages", resource="pages"),
            SpreeEndpointInfo("GET", "/api/v3/store/pages/:id", "Get page details", resource="pages"),
        ],
    ),
    
    "wishlists": SpreeResourceInfo(
        name="wishlists",
        base_path="/api/v3/store/wishlists",
        description="Wishlist endpoints",
        endpoints=[
            SpreeEndpointInfo("GET", "/api/v3/store/wishlists", "List user wishlists", requires_auth=True, resource="wishlists"),
            SpreeEndpointInfo("POST", "/api/v3/store/wishlists", "Create wishlist", requires_auth=True, resource="wishlists"),
            SpreeEndpointInfo("GET", "/api/v3/store/wishlists/default", "Get default wishlist", requires_auth=True, resource="wishlists"),
            SpreeEndpointInfo("GET", "/api/v3/store/wishlists/:token", "Get wishlist by token", resource="wishlists"),
            SpreeEndpointInfo("PATCH", "/api/v3/store/wishlists/:token", "Update wishlist", requires_auth=True, resource="wishlists"),
            SpreeEndpointInfo("DELETE", "/api/v3/store/wishlists/:token", "Delete wishlist", requires_auth=True, safe_for_coverage=False, resource="wishlists"),
            SpreeEndpointInfo("POST", "/api/v3/store/wishlists/:token/add_item", "Add item to wishlist", requires_auth=True, resource="wishlists"),
            SpreeEndpointInfo("DELETE", "/api/v3/store/wishlists/:token/remove_item/:id", "Remove item from wishlist", requires_auth=True, safe_for_coverage=False, resource="wishlists"),
        ],
    ),
    
    "auth": SpreeResourceInfo(
        name="auth",
        base_path="/api/v3/store/auth",
        description="Authentication endpoints",
        endpoints=[
            SpreeEndpointInfo("POST", "/api/v3/store/oauth/token", "Get OAuth token (login)", resource="auth"),
            SpreeEndpointInfo("POST", "/api/v3/store/oauth/revoke", "Revoke token (logout)", requires_auth=True, resource="auth"),
        ],
    ),
}


def get_all_endpoints() -> List[SpreeEndpointInfo]:
    """Get all Spree Store API endpoints."""
    endpoints = []
    for resource in SPREE_STORE_API_RESOURCES.values():
        endpoints.extend(resource.endpoints)
    return endpoints


def get_safe_endpoints() -> List[SpreeEndpointInfo]:
    """Get endpoints safe for coverage testing (excludes destructive operations)."""
    return [e for e in get_all_endpoints() if e.safe_for_coverage]


def get_public_endpoints() -> List[SpreeEndpointInfo]:
    """Get public endpoints that don't require authentication."""
    return [e for e in get_all_endpoints() if not e.requires_auth]


def get_endpoints_by_resource(resource_name: str) -> List[SpreeEndpointInfo]:
    """Get endpoints for a specific resource."""
    resource = SPREE_STORE_API_RESOURCES.get(resource_name)
    return resource.endpoints if resource else []


def format_endpoints_for_prompt(endpoints: List[SpreeEndpointInfo]) -> str:
    """Format endpoints into a string for LLM prompt."""
    lines = []
    
    current_resource = None
    for endpoint in endpoints:
        if endpoint.resource != current_resource:
            current_resource = endpoint.resource
            lines.append(f"\n## {current_resource.replace('_', ' ').title()}")
        
        auth_marker = " (requires auth)" if endpoint.requires_auth else ""
        safe_marker = "" if endpoint.safe_for_coverage else " [SKIP - destructive]"
        lines.append(f"  {endpoint.method} {endpoint.path}{auth_marker}{safe_marker}")
        if endpoint.description:
            lines.append(f"      # {endpoint.description}")
    
    return "\n".join(lines)


def get_api_statistics() -> Dict:
    """Get statistics about the API endpoints."""
    all_endpoints = get_all_endpoints()
    
    return {
        "total_resources": len(SPREE_STORE_API_RESOURCES),
        "total_endpoints": len(all_endpoints),
        "public_endpoints": len([e for e in all_endpoints if not e.requires_auth]),
        "authenticated_endpoints": len([e for e in all_endpoints if e.requires_auth]),
        "safe_endpoints": len([e for e in all_endpoints if e.safe_for_coverage]),
        "by_method": {
            "GET": len([e for e in all_endpoints if e.method == "GET"]),
            "POST": len([e for e in all_endpoints if e.method == "POST"]),
            "PATCH": len([e for e in all_endpoints if e.method == "PATCH"]),
            "DELETE": len([e for e in all_endpoints if e.method == "DELETE"]),
        },
    }
