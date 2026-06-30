from django.conf import settings

from store.models import Product

def artisan_global_data(request):
    if request.user.is_authenticated and request.user.is_artisan:
        return {
            'my_products': Product.objects.filter(artisan=request.user)
        }
    return {}


def site_marketing_data(request):
    return {
        'google_site_verification': settings.GOOGLE_SITE_VERIFICATION,
        'adsense_client_id': settings.ADSENSE_CLIENT_ID,
        'enable_adsense': bool(settings.ADSENSE_CLIENT_ID) and not settings.DEBUG,
    }
