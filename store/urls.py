from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('collection/', views.product_list, name='collection'), # Keep alias for now
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    
    # Cart & Checkout
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('cart/coupon/remove/', views.remove_coupon, name='remove_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),

    # Policies
    path('policies/privacy/', views.privacy_policy, name='privacy_policy'),
    path('policies/terms/', views.terms_of_service, name='terms_of_service'),
    path('policies/refund/', views.refund_policy, name='refund_policy'),
    path('policies/shipping/', views.shipping_policy, name='shipping_policy'),

    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('order/create/<int:pk>/', views.create_order, name='create_order'),
    path('order/track/', views.track_order_search, name='track_order_search'),
    path('order/track/<uuid:tracking_id>/', views.order_tracking, name='order_tracking'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('artisan/mobile/dashboard/', views.artisan_dashboard, name='artisan_dashboard'),
    path('artisan/add-review/', views.artisan_add_review, name='artisan_add_review'),
    path('artisan/stats/', views.artisan_stats, name='artisan_stats'),
    path('artisan/settings/', views.artisan_settings, name='artisan_settings'),
    path('artisan/payment-qr/', views.artisan_payment_qr, name='artisan_payment_qr'),
    path('artisan/orders/', views.artisan_orders, name='artisan_orders'),
    path('artisan/invoices/', views.artisan_invoices, name='artisan_invoices'),
    path('artisan/products/', views.artisan_products_list, name='artisan_products_list'),
    path('artisan/product/add/', views.add_product, name='add_product'),
    path('artisan/category/add/', views.artisan_add_category, name='artisan_add_category'),
    path('artisan/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('artisan/featured/', views.artisan_featured_items, name='artisan_featured_items'),
    path('artisan/product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('artisan/order/<int:pk>/manage/', views.manage_order, name='manage_order'),
    path('artisan/order/<int:pk>/start/', views.start_preparing, name='start_preparing'),
    path('artisan/order/<int:pk>/invoice/', views.download_invoice, name='download_invoice'),
    path('artisan/coupons/', views.artisan_coupons, name='artisan_coupons'),
    path('artisan/coupons/add/', views.add_coupon, name='add_coupon'),
    path('artisan/coupons/delete/<int:pk>/', views.delete_coupon, name='delete_coupon'),
    path('test/', views.test_page, name='test_page'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
]
