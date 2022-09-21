from django.http import HttpResponse
from django.views import View
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.generic import TemplateView
# from project.settings import STRIPE_WEBHOOK_SECRET
from .models import Product
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import json
from django.utils.decorators import method_decorator

stripe.api_key = settings.STRIPE_SECRET_KEY

# endpoint_secret = settings.STRIPE_WEBHOOK_SECRETE


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="T - shirt")
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({
            "product": product,
            "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY
        })
        return context


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs["pk"]
        product = Product.objects.get(id=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {'currency': 'inr',
                                   'unit_amount': product.price,
                                   'product_data': {'name': product.name}},
                    'quantity': 1,
                },
            ],
            metadata={"product_id": product.id},
            mode='payment',
            success_url=YOUR_DOMAIN + '/success/',
            cancel_url=YOUR_DOMAIN + '/cancel/',
        )
        return JsonResponse({'id': checkout_session.url}, safe=False)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    print(payload)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRETE
        )

    except ValueError as e:
        print('-------------------------------', e)
        return HttpResponse(status=400)


    except stripe.error.SignatureVerificationError as e:
        print('-------------------------------', e)
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.complete':
        session = event['data']['object']
        print(session)
    return HttpResponse(status=200)


@method_decorator(csrf_exempt, name="dispatch")
class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            product_id = self.kwargs["pk"]
            product = Product.objects.get(id=product_id)
            intent = stripe.PaymentIntent.create(
                amount=product.price,
                currency='inr',
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})
