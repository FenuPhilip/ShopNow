from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list_view, name='order_list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_view, name='payment'),
    path('confirmation/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    path('<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('<str:order_number>/cancel/', views.cancel_order_view, name='cancel_order'),
]
