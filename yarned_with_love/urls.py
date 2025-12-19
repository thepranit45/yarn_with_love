from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('users/', include('users.urls')),
    
    # Quick artist login routes
    path('mansi/', user_views.quick_artist_login, {'username': 'mansi', 'password': 'yarnbymansi'}, name='mansi_login'),
    path('pranit/', user_views.quick_artist_login, {'username': 'pranit', 'password': 'thepranit'}, name='pranit_login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
