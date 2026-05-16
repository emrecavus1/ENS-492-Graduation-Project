# Spree-Starter Test Generation Report

## 1. Code Coverage Summary

| Metric | Value |
|--------|-------|
| Total Resources | 15 |
| Total Endpoints | 46 |
| Zero Coverage Resources | 0 |
| Well Covered (>80%) | 12 |
| Overall Coverage | 95.7% |

### 1.1 Coverage by Resource

| Resource | Endpoints | Tests | Coverage | Auth Required |
|----------|-----------|-------|----------|---------------|
| products | 2 | 2 | 100.0% | 0 |
| taxons | 2 | 2 | 100.0% | 0 |
| account | 3 | 3 | 100.0% | 2 |
| account_orders | 2 | 2 | 100.0% | 2 |
| account_credit_cards | 1 | 1 | 100.0% | 1 |
| countries | 3 | 3 | 100.0% | 0 |
| states | 1 | 1 | 100.0% | 0 |
| stores | 1 | 1 | 100.0% | 0 |
| menus | 2 | 2 | 100.0% | 0 |
| pages | 2 | 2 | 100.0% | 0 |
| auth | 2 | 2 | 100.0% | 1 |
| checkout | 5 | 4 | 80.0% | 5 |
| cart | 8 | 6 | 75.0% | 7 |
| account_addresses | 4 | 3 | 75.0% | 4 |
| wishlists | 8 | 6 | 75.0% | 7 |

## 2. API Documentation

### 2.1 API Statistics

| Metric | Count |
|--------|-------|
| Total Resources | 15 |
| Total Endpoints | 46 |
| Public Endpoints | 17 |
| Authenticated Endpoints | 29 |
| Safe for Testing | 40 |
| Unsafe (filtered) | 6 |

### 2.2 Endpoints by HTTP Method

| Method | Count |
|--------|-------|
| GET | 23 |
| POST | 9 |
| PATCH | 9 |
| DELETE | 5 |

### 2.3 Resource Details


#### Products (`products`)
- Base Path: `/api/v3/store/products`
- Description: Product catalog endpoints
- Total Endpoints: 2
- Auth Required: 0
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/products` | List all products | No | Yes |
| GET | `/api/v3/store/products/:id` | Get product details | No | Yes |

#### Taxons (`taxons`)
- Base Path: `/api/v3/store/taxons`
- Description: Category/taxonomy endpoints
- Total Endpoints: 2
- Auth Required: 0
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/taxons` | List all taxons/categories | No | Yes |
| GET | `/api/v3/store/taxons/:id` | Get taxon details | No | Yes |

#### Cart (`cart`)
- Base Path: `/api/v3/store/cart`
- Description: Shopping cart endpoints
- Total Endpoints: 8
- Auth Required: 7
- Safe Endpoints: 6

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| POST | `/api/v3/store/cart` | Create a new cart | No | Yes |
| GET | `/api/v3/store/cart` | Get current cart | Yes | Yes |
| PATCH | `/api/v3/store/cart` | Update cart | Yes | Yes |
| DELETE | `/api/v3/store/cart` | Clear cart | Yes | No ⚠️ |
| POST | `/api/v3/store/cart/add_item` | Add item to cart | Yes | Yes |
| PATCH | `/api/v3/store/cart/set_quantity` | Set item quantity | Yes | Yes |
| DELETE | `/api/v3/store/cart/remove_line_item/:id` | Remove item from cart | Yes | No ⚠️ |
| POST | `/api/v3/store/cart/apply_coupon_code` | Apply coupon code | Yes | Yes |

#### Checkout (`checkout`)
- Base Path: `/api/v3/store/checkout`
- Description: Checkout flow endpoints
- Total Endpoints: 5
- Auth Required: 5
- Safe Endpoints: 4

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/checkout` | Get checkout state | Yes | Yes |
| PATCH | `/api/v3/store/checkout` | Update checkout | Yes | Yes |
| PATCH | `/api/v3/store/checkout/next` | Advance checkout state | Yes | Yes |
| PATCH | `/api/v3/store/checkout/advance` | Advance to furthest state | Yes | Yes |
| PATCH | `/api/v3/store/checkout/complete` | Complete checkout | Yes | No ⚠️ |

#### Account (`account`)
- Base Path: `/api/v3/store/account`
- Description: User account endpoints
- Total Endpoints: 3
- Auth Required: 2
- Safe Endpoints: 3

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/account` | Get current user account | Yes | Yes |
| PATCH | `/api/v3/store/account` | Update account | Yes | Yes |
| POST | `/api/v3/store/account` | Create account (register) | No | Yes |

#### Account Orders (`account_orders`)
- Base Path: `/api/v3/store/account/orders`
- Description: User order history endpoints
- Total Endpoints: 2
- Auth Required: 2
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/account/orders` | List user orders | Yes | Yes |
| GET | `/api/v3/store/account/orders/:id` | Get order details | Yes | Yes |

#### Account Addresses (`account_addresses`)
- Base Path: `/api/v3/store/account/addresses`
- Description: User address book endpoints
- Total Endpoints: 4
- Auth Required: 4
- Safe Endpoints: 3

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/account/addresses` | List user addresses | Yes | Yes |
| POST | `/api/v3/store/account/addresses` | Create address | Yes | Yes |
| PATCH | `/api/v3/store/account/addresses/:id` | Update address | Yes | Yes |
| DELETE | `/api/v3/store/account/addresses/:id` | Delete address | Yes | No ⚠️ |

#### Account Credit Cards (`account_credit_cards`)
- Base Path: `/api/v3/store/account/credit_cards`
- Description: Saved payment methods
- Total Endpoints: 1
- Auth Required: 1
- Safe Endpoints: 1

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/account/credit_cards` | List saved cards | Yes | Yes |

#### Countries (`countries`)
- Base Path: `/api/v3/store/countries`
- Description: Country data endpoints
- Total Endpoints: 3
- Auth Required: 0
- Safe Endpoints: 3

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/countries` | List all countries | No | Yes |
| GET | `/api/v3/store/countries/:iso` | Get country by ISO code | No | Yes |
| GET | `/api/v3/store/countries/default` | Get default country | No | Yes |

#### States (`states`)
- Base Path: `/api/v3/store/states`
- Description: State/province data endpoints
- Total Endpoints: 1
- Auth Required: 0
- Safe Endpoints: 1

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/states` | List all states | No | Yes |

#### Stores (`stores`)
- Base Path: `/api/v3/store/store`
- Description: Store information endpoints
- Total Endpoints: 1
- Auth Required: 0
- Safe Endpoints: 1

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/store` | Get current store info | No | Yes |

#### Menus (`menus`)
- Base Path: `/api/v3/store/menus`
- Description: Navigation menu endpoints
- Total Endpoints: 2
- Auth Required: 0
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/menus` | List all menus | No | Yes |
| GET | `/api/v3/store/menus/:id` | Get menu details | No | Yes |

#### Pages (`pages`)
- Base Path: `/api/v3/store/pages`
- Description: CMS pages endpoints
- Total Endpoints: 2
- Auth Required: 0
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/pages` | List all pages | No | Yes |
| GET | `/api/v3/store/pages/:id` | Get page details | No | Yes |

#### Wishlists (`wishlists`)
- Base Path: `/api/v3/store/wishlists`
- Description: Wishlist endpoints
- Total Endpoints: 8
- Auth Required: 7
- Safe Endpoints: 6

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| GET | `/api/v3/store/wishlists` | List user wishlists | Yes | Yes |
| POST | `/api/v3/store/wishlists` | Create wishlist | Yes | Yes |
| GET | `/api/v3/store/wishlists/default` | Get default wishlist | Yes | Yes |
| GET | `/api/v3/store/wishlists/:token` | Get wishlist by token | No | Yes |
| PATCH | `/api/v3/store/wishlists/:token` | Update wishlist | Yes | Yes |
| DELETE | `/api/v3/store/wishlists/:token` | Delete wishlist | Yes | No ⚠️ |
| POST | `/api/v3/store/wishlists/:token/add_item` | Add item to wishlist | Yes | Yes |
| DELETE | `/api/v3/store/wishlists/:token/remove_item/:id` | Remove item from wishlist | Yes | No ⚠️ |

#### Auth (`auth`)
- Base Path: `/api/v3/store/auth`
- Description: Authentication endpoints
- Total Endpoints: 2
- Auth Required: 1
- Safe Endpoints: 2

| Method | Path | Description | Auth | Safe |
|--------|------|-------------|------|------|
| POST | `/api/v3/store/oauth/token` | Get OAuth token (login) | No | Yes |
| POST | `/api/v3/store/oauth/revoke` | Revoke token (logout) | Yes | Yes |

## 3. Generated Test Cases

**Total Test Cases Generated:** 40

### 3.1 Test Case Summary

| # | Test Name | Resource | Method | Auth |
|---|-----------|----------|--------|------|
| 1 | returns a list of products | products | GET | No |
| 2 | returns product details | products | GET | No |
| 3 | returns a list of taxons | taxons | GET | No |
| 4 | returns taxon details | taxons | GET | No |
| 5 | creates a new cart | cart | POST | Yes |
| 6 | returns current cart for authenticated user | cart | GET | Yes |
| 7 | updates the cart | cart | PATCH | Yes |
| 8 | adds an item to the cart | cart | POST | Yes |
| 9 | sets item quantity in the cart | cart | PATCH | Yes |
| 10 | applies a coupon code to the cart | cart | POST | Yes |
| 11 | returns checkout state | checkout | GET | Yes |
| 12 | updates checkout | checkout | PATCH | Yes |
| 13 | advances checkout state | checkout | PATCH | Yes |
| 14 | advances to furthest checkout state | checkout | PATCH | Yes |
| 15 | creates a new account (register) | account | POST | Yes |
| 16 | returns current user account | account | GET | Yes |
| 17 | updates current user account | account | PATCH | Yes |
| 18 | lists user orders | account_orders | GET | Yes |
| 19 | returns order details | account_orders | GET | Yes |
| 20 | lists user addresses | account_addresses | GET | Yes |
| 21 | creates a new address | account_addresses | POST | Yes |
| 22 | updates an address | account_addresses | PATCH | Yes |
| 23 | lists saved credit cards | account_credit_cards | GET | Yes |
| 24 | returns a list of countries | countries | GET | No |
| 25 | returns country by ISO code | countries | GET | No |
| 26 | returns default country | countries | GET | No |
| 27 | returns a list of states | states | GET | No |
| 28 | returns current store info | stores | GET | No |
| 29 | returns a list of menus | menus | GET | No |
| 30 | returns menu details | menus | GET | No |
| 31 | returns a list of pages | pages | GET | No |
| 32 | returns page details | pages | GET | No |
| 33 | returns wishlist by token (public) | wishlists | GET | Yes |
| 34 | lists user wishlists (authenticated) | wishlists | GET | Yes |
| 35 | creates a wishlist (authenticated) | wishlists | POST | Yes |
| 36 | returns default wishlist (authenticated) | wishlists | GET | Yes |
| 37 | updates wishlist (authenticated) | wishlists | PATCH | Yes |
| 38 | adds item to wishlist (authenticated) | wishlists | POST | Yes |
| 39 | returns OAuth token (login) | auth | POST | Yes |
| 40 | revokes token (logout) (authenticated) | auth | POST | Yes |

### 3.2 Tests by Resource

| Resource | Test Count |
|----------|------------|
| cart | 6 |
| wishlists | 6 |
| checkout | 4 |
| account | 3 |
| account_addresses | 3 |
| countries | 3 |
| products | 2 |
| taxons | 2 |
| account_orders | 2 |
| menus | 2 |
| pages | 2 |
| auth | 2 |
| account_credit_cards | 1 |
| states | 1 |
| stores | 1 |

## 4. Coverage Gaps Analysis

### 4.1 What Couldn't Be Covered and Why

| Resource | Reason | Priority |
|----------|--------|----------|
| cart | Cart state-dependent operations need sequential setup (current: 75.0%) | MEDIUM |
| wishlists | Some wishlist operations need existing wishlist items (current: 75.0%) | MEDIUM |
| account_addresses | Address operations tested - some require existing address fixtures (current: 75.0%) | LOW |

### 4.2 Gap Summary

| Priority | Count |
|----------|-------|
| MEDIUM | 2 |
| LOW | 1 |
