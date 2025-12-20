from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Registration
    path('register/', views.register, name='register'),
    
    # Login
    path('login/', views.login_choice, name='login'),
    path('login/customer/', auth_views.LoginView.as_view(template_name='users/login_customer.html'), name='login_customer'),
    path('login/artist/', views.login_artist, name='login_artist'),
    path('login/admin/', views.login_admin, name='login_admin'),
    path('manage-access-codes/', views.manage_access_codes, name='manage_access_codes'),
]
