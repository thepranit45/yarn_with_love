from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from store.sitemaps import ProductSitemap, StaticViewSitemap
from users import views as user_views
from store import views as store_views

sitemaps = {
    'products': ProductSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('accounts/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # Direct login shortcuts (Keep these!)
    path('mansi/', user_views.quick_artist_login, {'username': 'mansi'}, name='mansi_login'),
    path('pranit/', user_views.quick_artist_login, {'username': 'pranit'}, name='pranit_login'),
    path('artisan/add-category/', store_views.add_category, name='add_category'),
    path('artisan/link-variant/<int:pk>/', store_views.link_variant, name='link_variant'),
    path('artisan/orders/', store_views.artisan_orders, name='artisan_orders'),
    path('default/', user_views.quick_artist_login, {'username': 'artisan_demo'}, name='default_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
