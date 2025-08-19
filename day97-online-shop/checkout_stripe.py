import stripe
import os
from flask import jsonify, redirect

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

if not stripe.api_key:
    raise EnvironmentError("STRIPE_SECRET_KEY environment variable is not set")


# Server functions to interact with Stripe (without defining routes, that'll happen in main.py
def create_checkout_session(cart_items, total_price):
    """
    Creates a custom Checkout session for Stripe's payment flow.
    Returns: client_secret that will be used in frontend to initialize Elements.
    """
    try:
        # Calcular el monto total incluyendo envío
        total_amount = int((total_price + 10) * 100)  # Añade $10 de envío y convierte a centavos

        # Crear la sesión de checkout con ui_mode="embedded"
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'oxxo'],  # Incluir OXXO como método de pago
            line_items=[
                {
                    'price_data': {
                        'currency': 'mxn',
                        'product_data': {
                            'name': item['name'],
                        },
                        'unit_amount': int(item['price'] * 100),  # Stripe maneja costos en centavos
                    },
                    'quantity': item['quantity'],
                } for item in cart_items
            ],
            mode='payment',
            ui_mode="embedded",  # Importante: esto habilita el modo integrado
            return_url="{url}/success?session_id={{CHECKOUT_SESSION_ID}}".format(
                url=os.environ.get('DOMAIN_URL', 'http://127.0.0.1:5001')
            ),
        )

        # Devolver el client_secret de la sesión
        return jsonify({
            'checkoutSessionClientSecret': session.client_secret
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


def create_payment_intent(cart_items, total_price):
    """
    Create a PaymentIntent to use with Elements
    """
    try:
        total_amount = int((total_price + 10) * 100)  # Añade $10 de envío y convierte a centavos

        # Metadata for PaymentIntent
        metadata = {
            'items': ', '.join([f"{item.get('name')} x{item.get('quantity')}" for item in cart_items])
        }

        # Create PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='mxn',
            payment_method_types=['card', 'oxxo'],
            metadata=metadata
        )

        print(f"PaymentIntent created: {intent.id}")
        print(f"Client Secret: {intent.client_secret}")

        return jsonify({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        import traceback
        print(f"Error creating payment intent: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 400


def retrieve_checkout_session(session_id):
    """
    Recovers information from a specific checkout session.
    Useful to verify the payment status in the success page.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except Exception as e:
        return None