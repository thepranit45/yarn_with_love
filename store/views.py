from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models import Q, Prefetch
from .models import Product, Order, OrderItem, OrderUpdate, Review, Category, Subscriber, Cart, CartItem
from .forms import OrderUpdateForm, OrderStatusForm, ProductForm, ReviewForm
from django.contrib import messages
import uuid
import razorpay
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET"])
def product_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True).select_related('artisan', 'category')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    
    categories = Category.objects.all()
    
    return render(request, 'store/product_list.html', {
        'products': products, 
        'query': query,
        'categories': categories
    })

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('artisan').prefetch_related('reviews'), pk=pk)
    reviews = product.reviews.select_related('customer')
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    related_products = Product.objects.filter(is_active=True, category=product.category).exclude(pk=pk)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products
    })

@login_required
@require_http_methods(["GET", "POST"])
def create_order(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    if request.method == 'POST':
        notes = request.POST.get('customization_notes', '').strip()
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            messages.error(request, "Quantity must be at least 1.")
            return redirect('product_detail', pk=pk)
        
        try:
            # Create Order
            order = Order.objects.create(
                customer=request.user,
                status='PENDING',
                customization_notes=notes
            )
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_purchase=product.price
            )
            messages.success(request, "Order placed successfully!")
            return redirect('order_tracking', tracking_id=order.tracking_id)
        except Exception as e:
            messages.error(request, "Error creating order. Please try again.")
            return redirect('product_detail', pk=pk)
    
    return render(request, 'store/create_order.html', {'product': product})

def order_tracking(request, tracking_id):
    try:
        order = get_object_or_404(Order.objects.prefetch_related('items', 'updates'), tracking_id=tracking_id)
    except:
        messages.error(request, "Order not found.")
        return redirect('track_order_search')
    
    progress_width = order.get_progress_percentage()
    total_price = order.get_total_price()
    
    return render(request, 'store/order_tracking.html', {
        'order': order,
        'progress_width': progress_width,
        'total_price': total_price
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).prefetch_related('items__product')
    
    # Add total price to each order for display
    for order in orders:
        order.total_price = order.get_total_price()
    
    return render(request, 'store/my_orders.html', {'orders': orders})

@require_http_methods(["GET", "POST"])
def track_order_search(request):
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id', '').strip()
        
        if tracking_id:
            try:
                # Validate UUID format before redirecting to avoid NoReverseMatch or 404
                uuid.UUID(tracking_id)
                return redirect('order_tracking', tracking_id=tracking_id)
            except ValueError:
                messages.error(request, "Please enter a valid Tracking ID (format: 123e4567-e89b-12d3-a456-426614174000).")
        else:
            messages.error(request, "Please enter a Tracking ID.")
            
    return render(request, 'store/track_order_search.html')

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_dashboard(request):
    # Pending Order Stack
    pending_orders = Order.objects.filter(status='PENDING').prefetch_related('items__product')
    # All other active orders
    active_orders = Order.objects.exclude(status__in=['PENDING', 'COMPLETED', 'CANCELLED']).prefetch_related('items__product')
    completed_orders = Order.objects.filter(status__in=['COMPLETED', 'CANCELLED']).order_by('-updated_at')[:5]
    
    # Dashboard Stats
    total_orders = Order.objects.count()
    total_customers = Order.objects.values('customer').distinct().count()
    
    # Calculate Total Revenue (only from Completed/Shipped orders for accuracy, or all non-cancelled)
    revenue_orders = Order.objects.exclude(status='CANCELLED').prefetch_related('items')
    total_revenue = int(sum(order.get_total_price() for order in revenue_orders))

    return render(request, 'store/artisan_dashboard.html', {
        'pending_orders': pending_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
    })

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_stats(request):
    """Dedicated statistics page for artisans"""
    # Totals for Cards (re-calculated for context if needed, or just charts)
    total_orders = Order.objects.count()
    total_customers = Order.objects.values('customer').distinct().count()
    
    revenue_orders = Order.objects.exclude(status='CANCELLED').prefetch_related('items')
    total_revenue = int(sum(order.get_total_price() for order in revenue_orders))

    # Chart Data
    pending_count = Order.objects.filter(status='PENDING').count()
    active_count = Order.objects.exclude(status__in=['PENDING', 'COMPLETED', 'CANCELLED']).count()
    completed_count = Order.objects.filter(status__in=['COMPLETED', 'CANCELLED']).count()

    return render(request, 'store/artisan_stats.html', {
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'pending_count': pending_count,
        'active_count': active_count,
        'completed_count': completed_count,
    })

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["GET", "POST"])
def manage_order(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__product', 'updates'), pk=pk)
    
    status_form = OrderStatusForm(instance=order)
    update_form = OrderUpdateForm()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            status_form = OrderStatusForm(request.POST, instance=order)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, f"Order status updated to {order.get_status_display()}")
                return redirect('manage_order', pk=pk)
        elif 'post_update' in request.POST:
            update_form = OrderUpdateForm(request.POST, request.FILES)
            if update_form.is_valid():
                try:
                    update = update_form.save(commit=False)
                    update.order = order
                    update.save()
                    messages.success(request, "Story update posted!")
                except Exception as e:
                    messages.error(request, "Error posting update. Please try again.")
                return redirect('manage_order', pk=pk)

    return render(request, 'store/manage_order.html', {
        'order': order,
        'status_form': status_form,
        'update_form': update_form
    })

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["GET", "POST"])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.artisan = request.user
                product.save()
                messages.success(request, "Product added successfully!")
                return redirect('product_detail', pk=product.pk)
            except Exception as e:
                messages.error(request, "Error creating product. Please try again.")
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})


@login_required
@require_http_methods(["POST"])
def add_review(request, pk):
    """Add or update a review for a product"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    # Check if customer has a previous order for this product
    has_ordered = Order.objects.filter(
        customer=request.user,
        items__product=product,
        status='COMPLETED'
    ).exists()
    
    if not has_ordered:
        messages.error(request, "You can only review products you've ordered.")
        return redirect('product_detail', pk=pk)
    
    rating = request.POST.get('rating', '')
    comment = request.POST.get('comment', '').strip()
    
    try:
        review, created = Review.objects.update_or_create(
            product=product,
            customer=request.user,
            defaults={'rating': int(rating), 'comment': comment}
        )
        if created:
            messages.success(request, "Review posted successfully!")
        else:
            messages.success(request, "Review updated successfully!")
    except Exception as e:
        messages.error(request, "Error posting review. Please try again.")
    
    return redirect('product_detail', pk=pk)

@require_http_methods(["POST"])
def subscribe(request):
    email = request.POST.get('email')
    if email:
        if Subscriber.objects.filter(email=email).exists():
            messages.warning(request, 'You are already subscribed to our newsletter.')
        else:
            Subscriber.objects.create(email=email)
            messages.success(request, 'Thank you for subscribing! 💌')
    else:
        messages.error(request, 'Please provide a valid email address.')
    return redirect('product_list')

@login_required
@require_http_methods(["POST"])
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity', 1))
    notes = request.POST.get('customization_notes', '').strip()

    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if item already exists with same customization (optional, for now just simplistic)
    # We will simply add or update quantity if same product in cart.
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    
    # Update notes if provided (overwrites previous if existing item)
    if notes:
        cart_item.customization_notes = notes
        
    cart_item.save()
    
    action = request.POST.get('action', 'add_to_cart')
    if action == 'buy_now':
        return redirect('checkout')
        
    messages.success(request, f"{product.name} added to cart! 🛒")
    return redirect('product_detail', pk=pk)

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')
    
    # Simple check to avoid errors if prices are large
    total_amount = float(cart.get_total_price())
    
    # Razorpay Order Creation
    currency = 'INR'
    amount = int(total_amount * 100) # Amount in paise
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    razorpay_order = client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': '1'
    })
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'total_amount': total_amount
    })

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            # In a real scenario, VERIFY signature here using client.utility.verify_payment_signature()
            
            cart = Cart.objects.get(user=request.user)
            
            with transaction.atomic():
                order = Order.objects.create(
                    customer=request.user,
                    status='PENDING',
                    customization_notes="Paid via Razorpay"
                )
                
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price_at_purchase=item.product.price
                    )
                
                # Clear Cart
                cart.items.all().delete()
                
            messages.success(request, "Payment Successful! Order placed. 🎉")
            return redirect('order_tracking', tracking_id=order.tracking_id)
            
        except Exception as e:
            messages.error(request, "Payment Failed or Error processing order.")
            return redirect('view_cart')
    return redirect('view_cart')

# Policy Views
def privacy_policy(request):
    return render(request, 'store/policies/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'store/policies/terms_and_conditions.html')

def refund_policy(request):
    return render(request, 'store/policies/refund_policy.html')

def shipping_policy(request):
    return render(request, 'store/policies/shipping_policy.html')

def contact_us(request):
    return render(request, 'store/policies/contact_us.html')






@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_products_list(request):
    """List all products for the artisan with management options"""
    # Show ALL products to any artisan (since they are a team)
    products = Product.objects.all().order_by('-created_at')
    
    # Search functionality
    query = request.GET.get('q', '')
    if query:
        products = products.filter(name__icontains=query)
        
    return render(request, 'store/artisan_products_list.html', {'products': products, 'query': query})

@login_required
@user_passes_test(lambda u: u.is_artisan)
def edit_product(request, pk):
    """Edit an existing product"""
    # Allow any artisan to edit any product
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('artisan_products_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'store/add_product.html', {
        'form': form, 
        'title': 'Edit Product',
        'is_edit': True
    })

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["POST"])
def delete_product(request, pk):
    """Delete a product"""
    # Allow any artisan to delete any product
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect('artisan_products_list')
