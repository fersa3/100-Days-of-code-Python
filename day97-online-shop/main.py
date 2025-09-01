from flask import Flask, abort, redirect, url_for, jsonify, render_template, request, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, AddToCartForm, FlaskForm
from online_shop_db import *
from checkout_stripe import create_checkout_session, retrieve_checkout_session, create_payment_intent
from datetime import datetime
import time

# 1: Create login and signing .htmls
# 2: Set up functional navigation between pages. (Only use objects displayed in home to keep it simple).
# 3: Implement users functionality.
# 4: Available objects db. List of clothes, sizes & prices.
# 5: Populate home page with available products from the dummy db.
# 6: Links to product detail and add to cart.
# 7: Functional cart. Interact with the db.
# 8: Add checkout functionality. Interact with the db.
    # Integrate payment info from Stripe in the Payment section in checkout route. Build a checkout page with embedded components: https://docs.stripe.com/checkout/custom/quickstart

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI_challenges', 'sqlite:///online_shop.db')
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize with app
db.init_app(app)
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configue Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Initialize database with app context and use database
with app.app_context():
    engine = init_db(app)
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Create an admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)
    return decorated_function()

# Context processor to make the cart count available to all templates
@app.context_processor
def inject_cart_count():
    cart_count = 0
    if 'cart' in session:
        cart_count = sum(int(item.get('quantity', 1)) for item in session['cart'])
    return {'cart_count': cart_count}


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user email is already present in the database:
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()

        if user:
            # User already exists
            flash("You've already singed up with that email. Log in instead.")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            username=form.username.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique, so will only return 1 result.
        user = result.scalar()
        if not user:
        # Email doesn't exist
            flash("That email is not registered yet, please sign in.")
            return redirect(url_for('register'))  # Redirect, causing a new request cycle
        elif not check_password_hash(user.password, password):
        # Password incorrect
            flash("Password incorrect, please try again")
            return redirect(url_for('login'))
        else:
            login_user(user)

            # Check if there's a pending cart item
            if 'pending_cart_item' in session:
                if 'cart' not in session:
                    session['cart'] = []
                session['cart'].append(session.pop('pending_cart_item'))
                session.modified = True  # Ensure session updates
                flash("Item added to cart after login!")
                return redirect(url_for('add_to_cart'))  # Redirect user to cart after login
            return redirect(url_for('home'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    session.pop('cart', None)
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))


@app.route('/')
def home():
    result = db.session.execute(db.select(Product))
    products = result.scalars().all()
    return render_template('index.html', products=products, current_user=current_user)



@app.route('/detail_product/<int:product_id>', methods=["GET", "POST"])
def go_to_detail(product_id):
    print(f"Request method: {request.method}")
    print(f"Form submitted: {request.form}")
    requested_product = db.get_or_404(Product, product_id)

    # Fetch sizes from product_sizes table where qty_in_stock is greater than 0
    available_sizes = get_available_sizes(product_id)

    # Create the form with dynamic choices
    form = setup_cart_form(product_id, available_sizes, requested_product.colors.split())

    # Handle form submission
    if form.validate_on_submit():
        cart_item = {
            "product_id": product_id,
            "size": form.size.data,
            "quantity": form.quantity.data,
            "color": form.color.data
        }

        # Check if user is logged in
        if not current_user.is_authenticated:
            # Save pending cart item and redirect to log in
            print(f"Storing pending cart item: {cart_item}")
            session['pending_cart_item'] =  cart_item
            session.modified = True
            flash("Please log in to continue.")
            return redirect(url_for('login'))

        # Add item to cart
        add_item_to_cart(cart_item)
        flash("Item added to cart!")
        return redirect(url_for('add_to_cart'))

    return render_template(
        'detail.html',
        product=requested_product,
        available_sizes=available_sizes,
        current_user=current_user,
        form=form
    )


@app.route('/add_to_cart', methods=["GET", "POST"])
def add_to_cart():
    cart_items, total_price = get_session_cart_items_and_total_price()
    form = FlaskForm()

    return render_template('cart.html', cart_items=cart_items, total_price=total_price, cart=bool(cart_items), form=form)


@app.route('/update_cart', methods=["POST"])
def update_cart():
    data = request.json
    product_id = int(data['product_id'])
    quantity = int(data['quantity'])

    # Update quantity in session
    if 'cart' in session:
        for item in session['cart']:
            if item['product_id'] == product_id:
                item['quantity'] = quantity
                session.modified = True
                break

    # Get product price to calculate totals
    product = db.get_or_404(Product, product_id)
    item_total = product.price * quantity

    # Calculate new subtotal
    subtotal = sum(db.get_or_404(Product, item['product_id']).price * int(item['quantity'])
                   for item in session['cart'])

    # Calculate grand total (subtotal + shipping)
    grand_total = subtotal + 10

    return jsonify({
        'success': True,
        'item_total': item_total,
        'subtotal': subtotal,
        'grand_total': grand_total
    })


@app.route('/remove_from_cart', methods=["POST"])
def remove_from_cart():
    data = request.json
    product_id = int(data['product_id'])

    # Remove item from session
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['product_id'] != product_id]
        session.modified = True

    # Check if cart is now empty
    cart_empty = len(session.get('cart', [])) == 0

    # Calculate new subtotal if cart is not empty
    subtotal = 0
    if not cart_empty:
        subtotal = sum(db.get_or_404(Product, item['product_id']).price * int(item['quantity'])
                       for item in session['cart'])

    # Calculate grand total (subtotal + shipping)
    grand_total = subtotal + 10 if not cart_empty else 0

    return jsonify({
        'success': True,
        'subtotal': subtotal,
        'grand_total': grand_total,
        'cart_empty': cart_empty
    })


@app.route('/checkout')
def go_to_checkout():
    cart_items, total_price = get_session_cart_items_and_total_price()
    stripe_public_key = os.environ.get("STRIPE_PUBLISHABLE_KEY")

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, stripe_key=stripe_public_key)

@app.route('/create-checkout-session', methods=['POST'])
def start_checkout():
    cart_items, total_price = get_session_cart_items_and_total_price()
    # Create the checkout session with Stripe
    return create_checkout_session(cart_items, total_price)

@app.route('/create-payment-intent', methods=['POST'])
def create_intent():
    cart_items, total_price = get_session_cart_items_and_total_price()
    return create_payment_intent(cart_items, total_price)

@app.route('/success')
def successful_payment():
    from flask import session
    # Recover the session data to verify the payment:
    session_id = request.args.get('session_id')
    cart_items, total_price = get_session_cart_items_and_total_price()

    if session_id:
        session = retrieve_checkout_session(session_id)
        payment_status = session.payment_status if session else 'unknown'
    else:
        payment_status = 'completed'  # Default if no session_id

    # Empty cart once payment has been confirmed successful
    if payment_status == 'paid' or payment_status == 'completed':
        # Store data from purchase in a variable
        purchase_data = {
            'products': cart_items,
            'total': total_price,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'order_id': session_id or f"ORDER-{int(time.time())}"
        }

        # Empty cart
        if 'cart' in session:
            session.pop('cart', None)
            session.modified = True

        return render_template('success.html',
                               current_user=current_user,
                               payment_status=payment_status,
                               purchase=purchase_data)
    else:
        return redirect(url_for('processing'))

@app.route('/processing')
def processing():
    # For payments with additional action required, like OXXO.
    return render_template('processing.html', current_user=current_user)

@app.route('/cancel')
def cancel_payment():
    return render_template('cancel.html', current_user=current_user)



# HELPER FUNCTIONS
def get_available_sizes(product_id):
    """ Get sizes with available stock for a product. """
    size_query = ProductSize.query.filter(
        ProductSize.product_id == product_id,
        ProductSize.qty_in_stock > 0
    ).with_entities(ProductSize.size).all()

    # Extract just the size values
    clean_sizes = [size.size for size in size_query]

    return clean_sizes


def setup_cart_form(product_id, size_values, color_options):
    """ Create and configura the cart form with dynamic choices. """
    form = AddToCartForm()
    form.product_id.data = product_id
    form.size.choices = [(size[0], size[0]) for size in size_values]
    form.color.choices = [(color, color) for color in color_options]
    return form


def add_item_to_cart(cart_item):
    """ Add an item to the session cart. """
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(cart_item)
    session.modified = True  # Ensure session updates


def get_session_cart_items_and_total_price():
    cart_items = []
    total_price = 0

    if 'cart' in session and session['cart']:
        # Get the actual products from the db based on the IDs in the cart
        for item in session['cart']:
            product = db.get_or_404(Product, item['product_id'])
            cart_item = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'image': product.image,
                'quantity': item['quantity'],
                'size': item['size'],
                'color': item['color']
            }
            cart_items.append(cart_item)
            total_price += product.price * int(item['quantity'])
    total_price = round(total_price, 2)

    return cart_items, total_price



if __name__ == "__main__":
    app.run(debug=True, port=5001)
