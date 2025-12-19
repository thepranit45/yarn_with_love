from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/review/', views.add_review, name='add_review'),
    path('order/create/<int:pk>/', views.create_order, name='create_order'),
    path('order/track/', views.track_order_search, name='track_order_search'),
    path('order/track/<uuid:tracking_id>/', views.order_tracking, name='order_tracking'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('artisan/mobile/dashboard/', views.artisan_dashboard, name='artisan_dashboard'),
    path('artisan/order/<int:pk>/manage/', views.manage_order, name='manage_order'),
    path('artisan/product/add/', views.add_product, name='add_product'),
]
