from django.urls import path
from . import views

urlpatterns = [
    path('stk-push/', views.stk_push, name='stk_push'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('check-payment-status/', views.check_payment_status, name='check_payment_status'),
]