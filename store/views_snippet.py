
@require_http_methods(["GET"])
def search_suggestions(request):
    query = request.GET.get('term', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)
    
    # Search for products matching the query
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(category__name__icontains=query)
    ).values('name', 'id')[:5]
    
    results = []
    for p in products:
        results.append({
            'label': p['name'],
            'value': p['name'],
            'url': f"/product/{p['id']}/"
        })
    
    return JsonResponse(results, safe=False)
