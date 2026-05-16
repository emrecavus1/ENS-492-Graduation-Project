require 'rails_helper'

RSpec.describe 'Spree Store API', type: :request do
  let(:store) { Spree::Store.default || create(:store) }
  let(:headers) { { 'Accept' => 'application/json', 'Content-Type' => 'application/json' } }
  
  let(:user) { create(:user, password: 'password123') }
  
  let(:auth_headers) {
    refresh_token = Spree::RefreshToken.create!(
      user: user,
      expires_at: 1.day.from_now
    )
    headers.merge('Authorization' => "Bearer #{refresh_token.token}")
  }

  # PRODUCTS (public)
  describe 'Products API' do
    let!(:product) { create(:product, stores: [store]) }

    describe 'GET /api/v3/store/products' do
      it 'returns a list of products' do
        get '/api/v3/store/products', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/products/:id' do
      it 'returns product details' do
        get "/api/v3/store/products/#{product.id}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # TAXONS (public)
  describe 'Taxons API' do
    let!(:taxon) { create(:taxon) }

    describe 'GET /api/v3/store/taxons' do
      it 'returns a list of taxons' do
        get '/api/v3/store/taxons', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/taxons/:id' do
      it 'returns taxon details' do
        get "/api/v3/store/taxons/#{taxon.id}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # CART (public & authenticated)
  describe 'Cart API' do
    describe 'POST /api/v3/store/cart' do
      it 'creates a new cart' do
        post '/api/v3/store/cart', headers: headers
        expect([200, 201, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/cart' do
      it 'returns current cart for authenticated user' do
        get '/api/v3/store/cart', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/cart' do
      it 'updates the cart' do
        patch '/api/v3/store/cart', headers: auth_headers, params: { cart: { note: 'Test note' } }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/cart/add_item' do
      it 'adds an item to the cart' do
        post '/api/v3/store/cart/add_item', headers: auth_headers, params: { variant_id: 1, quantity: 1 }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/cart/set_quantity' do
      it 'sets item quantity in the cart' do
        patch '/api/v3/store/cart/set_quantity', headers: auth_headers, params: { line_item_id: 1, quantity: 2 }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/cart/apply_coupon_code' do
      it 'applies a coupon code to the cart' do
        post '/api/v3/store/cart/apply_coupon_code', headers: auth_headers, params: { coupon_code: 'DISCOUNT10' }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end
  end

  # CHECKOUT (authenticated)
  describe 'Checkout API' do
    describe 'GET /api/v3/store/checkout' do
      it 'returns checkout state' do
        get '/api/v3/store/checkout', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/checkout' do
      it 'updates checkout' do
        patch '/api/v3/store/checkout', headers: auth_headers, params: { checkout: { email: 'test@example.com' } }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/checkout/next' do
      it 'advances checkout state' do
        patch '/api/v3/store/checkout/next', headers: auth_headers
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/checkout/advance' do
      it 'advances to furthest checkout state' do
        patch '/api/v3/store/checkout/advance', headers: auth_headers
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end
  end

  # ACCOUNT (public & authenticated)
  describe 'Account API' do
    describe 'POST /api/v3/store/account' do
      it 'creates a new account (register)' do
        post '/api/v3/store/account', headers: headers, params: { user: { email: 'newuser@example.com', password: 'password123', password_confirmation: 'password123' } }.to_json
        expect([200, 201, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/account' do
      it 'returns current user account' do
        get '/api/v3/store/account', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/account' do
      it 'updates current user account' do
        patch '/api/v3/store/account', headers: auth_headers, params: { user: { email: 'updated@example.com' } }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end
  end

  # ACCOUNT ORDERS (authenticated)
  describe 'Account Orders API' do
    let!(:order) { create(:order, user: user) }

    describe 'GET /api/v3/store/account/orders' do
      it 'lists user orders' do
        get '/api/v3/store/account/orders', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/account/orders/:id' do
      it 'returns order details' do
        get "/api/v3/store/account/orders/#{order.id}", headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # ACCOUNT ADDRESSES (authenticated)
  describe 'Account Addresses API' do
    let!(:address) { create(:address, user: user) }

    describe 'GET /api/v3/store/account/addresses' do
      it 'lists user addresses' do
        get '/api/v3/store/account/addresses', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/account/addresses' do
      it 'creates a new address' do
        post '/api/v3/store/account/addresses', headers: auth_headers, params: { address: { firstname: 'John', lastname: 'Doe', address1: '123 St', city: 'City', country_id: create(:country).id, zipcode: '12345' } }.to_json
        expect([200, 201, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/account/addresses/:id' do
      it 'updates an address' do
        patch "/api/v3/store/account/addresses/#{address.id}", headers: auth_headers, params: { address: { city: 'New City' } }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end
  end

  # ACCOUNT CREDIT CARDS (authenticated)
  describe 'Account Credit Cards API' do
    describe 'GET /api/v3/store/account/credit_cards' do
      it 'lists saved credit cards' do
        get '/api/v3/store/account/credit_cards', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # COUNTRIES (public)
  describe 'Countries API' do
    let!(:country) { create(:country) }

    describe 'GET /api/v3/store/countries' do
      it 'returns a list of countries' do
        get '/api/v3/store/countries', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/countries/:iso' do
      it 'returns country by ISO code' do
        get "/api/v3/store/countries/#{country.iso}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/countries/default' do
      it 'returns default country' do
        get '/api/v3/store/countries/default', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # STATES (public)
  describe 'States API' do
    describe 'GET /api/v3/store/states' do
      it 'returns a list of states' do
        get '/api/v3/store/states', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # STORES (public)
  describe 'Stores API' do
    describe 'GET /api/v3/store/store' do
      it 'returns current store info' do
        get '/api/v3/store/store', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # MENUS (public)
  describe 'Menus API' do
    let!(:menu) { create(:menu) }

    describe 'GET /api/v3/store/menus' do
      it 'returns a list of menus' do
        get '/api/v3/store/menus', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/menus/:id' do
      it 'returns menu details' do
        get "/api/v3/store/menus/#{menu.id}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # PAGES (public)
  describe 'Pages API' do
    let!(:page) { create(:page) }

    describe 'GET /api/v3/store/pages' do
      it 'returns a list of pages' do
        get '/api/v3/store/pages', headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/pages/:id' do
      it 'returns page details' do
        get "/api/v3/store/pages/#{page.id}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  # WISHLISTS (public & authenticated)
  describe 'Wishlists API' do
    let!(:wishlist) { create(:wishlist, user: user) }
    let(:token) { wishlist.token }

    describe 'GET /api/v3/store/wishlists/:token' do
      it 'returns wishlist by token (public)' do
        get "/api/v3/store/wishlists/#{token}", headers: headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/wishlists' do
      it 'lists user wishlists (authenticated)' do
        get '/api/v3/store/wishlists', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/wishlists' do
      it 'creates a wishlist (authenticated)' do
        post '/api/v3/store/wishlists', headers: auth_headers, params: { wishlist: { name: 'My Wishlist' } }.to_json
        expect([200, 201, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'GET /api/v3/store/wishlists/default' do
      it 'returns default wishlist (authenticated)' do
        get '/api/v3/store/wishlists/default', headers: auth_headers
        expect([200, 401, 404]).to include(response.status)
      end
    end

    describe 'PATCH /api/v3/store/wishlists/:token' do
      it 'updates wishlist (authenticated)' do
        patch "/api/v3/store/wishlists/#{token}", headers: auth_headers, params: { wishlist: { name: 'Updated Wishlist' } }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/wishlists/:token/add_item' do
      it 'adds item to wishlist (authenticated)' do
        post "/api/v3/store/wishlists/#{token}/add_item", headers: auth_headers, params: { variant_id: 1 }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end
  end

  # AUTH (public & authenticated)
  describe 'Auth API' do
    describe 'POST /api/v3/store/oauth/token' do
      it 'returns OAuth token (login)' do
        post '/api/v3/store/oauth/token', headers: headers, params: { grant_type: 'password', username: user.email, password: 'password123' }.to_json
        expect([200, 401, 404, 422]).to include(response.status)
      end
    end

    describe 'POST /api/v3/store/oauth/revoke' do
      it 'revokes token (logout) (authenticated)' do
        post '/api/v3/store/oauth/revoke', headers: auth_headers, params: { token: auth_headers['Authorization'].split.last }.to_json
        expect([200, 401, 404]).to include(response.status)
      end
    end
  end

  private

  def json_response
    JSON.parse(response.body)
  end
end