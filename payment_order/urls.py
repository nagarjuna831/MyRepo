from django.urls import path

from .views import *

urlpatterns = [
    path('pay/', StartPayment.as_view(), name="payment"),
    path('payment/success/',HandlePaymentSuccess.as_view(), name="payment_success"),
    path('message/',HandlePaymentSuccessMessage.as_view(), name="payment_success_message"),
]
