from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Cart & Checkout
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),

    # Policies
    path('policies/privacy/', views.privacy_policy, name='privacy_policy'),
    path('policies/terms/', views.terms_of_service, name='terms_of_service'),
    path('policies/refund/', views.refund_policy, name='refund_policy'),
    path('policies/shipping/', views.shipping_policy, name='shipping_policy'),
    path('contact/', views.contact_us, name='contact_us'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('order/create/<int:pk>/', views.create_order, name='create_order'),
    path('order/track/', views.track_order_search, name='track_order_search'),
    path('order/track/<uuid:tracking_id>/', views.order_tracking, name='order_tracking'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('artisan/mobile/dashboard/', views.artisan_dashboard, name='artisan_dashboard'),
    path('artisan/order/<int:pk>/manage/', views.manage_order, name='manage_order'),
    path('artisan/product/add/', views.add_product, name='add_product'),
]
