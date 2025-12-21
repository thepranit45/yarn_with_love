from store.models import Product

def artisan_global_data(request):
    if request.user.is_authenticated and request.user.is_artisan:
        return {
            'my_products': Product.objects.filter(artisan=request.user)
        }
    return {}
