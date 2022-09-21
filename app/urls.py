from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductLandingPageView.as_view(), name="landing-page"),
    path('create-checkout-session/<int:pk>/', views.CreateCheckoutSessionView.as_view(), name="checkout-session"),
    path('cancel/', views.CancelView.as_view(), name="cancel"),
    path('success/', views.SuccessView.as_view(), name="success"),
    path('webhook/', views.stripe_webhook, name="stripe_webhook"),
    path('create-payment-intent/<int:pk>/', views.StripeIntentView.as_view(), name="create-payment-intent"),
]
