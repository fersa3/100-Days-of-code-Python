// checkout.js - Implementación con PaymentIntents
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        // Inicializar Stripe con la clave pública
        const stripe = Stripe(stripePublicKey);

        // Elementos y variables del DOM
        const payButton = document.getElementById('pay-button');
        const paymentElement = document.getElementById('payment-element');
        const paymentErrorsDiv = document.getElementById('payment-errors');

        // Configurar los elementos de Stripe
        let elements;
        let paymentElementInstance;

        // Iniciar el proceso de checkout
        initCheckout();

        async function initCheckout() {
            try {
                console.log("Iniciando checkout con PaymentIntent...");

                // Paso 1: Crear un PaymentIntent desde el servidor
                const response = await fetch('/create-payment-intent', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const data = await response.json();
                console.log("Respuesta recibida:", data);

                if (data.error) {
                    showError(data.error);
                    return;
                }

                // Paso 2: Obtener el client_secret del PaymentIntent
                const clientSecret = data.clientSecret;
                console.log("Client secret:", clientSecret);

                if (!clientSecret) {
                    showError('No se pudo obtener la información necesaria para procesar el pago.');
                    return;
                }

                // Paso 3: Configurar Stripe Elements con el client_secret
                elements = stripe.elements({
                    clientSecret,
                    appearance: {
                        theme: 'stripe',
                        variables: {
                            colorPrimary: '#696cff',
                            colorBackground: '#ffffff',
                            colorText: '#30313d',
                        }
                    },
                    locale: 'es'
                });

                // Paso 4: Crear y montar el elemento de pago
                paymentElementInstance = elements.create('payment', {
                    layout: 'tabs',
                    paymentMethodOrder: ['card', 'oxxo']
                });

                paymentElementInstance.mount('#payment-element');

                // Paso 5: Configurar el evento de clic en el botón de pago
                if (payButton) {
                    payButton.addEventListener('click', handleSubmit);
                    // Habilitar el botón una vez que todo está listo
                    payButton.disabled = false;
                }
            } catch (error) {
                console.error("Error completo:", error);
                showError('Hubo un problema al cargar el formulario de pago. Por favor, inténtalo de nuevo.');
            }
        }

        // Manejar el envío del formulario
        async function handleSubmit(e) {
            e.preventDefault();

            if (!elements || !paymentElementInstance) {
                showError('El formulario de pago no está listo. Por favor, recarga la página.');
                return;
            }

            // Deshabilitar el botón durante el procesamiento
            payButton.disabled = true;
            payButton.textContent = 'Procesando...';

            try {
                // Confirmar el pago
                const { error } = await stripe.confirmPayment({
                    elements,
                    confirmParams: {
                        return_url: window.location.origin + '/success',
                    }
                });

                if (error) {
                    // Mostrar el error al usuario
                    showError(error.message);
                    // Habilitar el botón nuevamente
                    payButton.disabled = false;
                    payButton.textContent = 'Place Order';
                }
                // Si no hay error, se redirige al return_url
            } catch (err) {
                console.error('Error al procesar el pago:', err);
                showError('Ocurrió un error inesperado. Por favor, inténtalo de nuevo.');
                payButton.disabled = false;
                payButton.textContent = 'Place Order';
            }
        }

        // Función para mostrar mensajes de error
        function showError(message) {
            if (paymentErrorsDiv) {
                paymentErrorsDiv.textContent = message;
                paymentErrorsDiv.style.display = 'block';
            } else {
                console.error(message);
                alert(message);
            }
        }
    });
})();