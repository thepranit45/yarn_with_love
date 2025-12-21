from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models import Q, Prefetch
from .models import Product, Order, OrderItem, OrderUpdate, Review, Category, Subscriber, Cart, CartItem, Coupon, ChatInquiry
from .forms import OrderUpdateForm, OrderStatusForm, ProductForm, ReviewForm, CheckoutForm, CouponForm
from django.contrib import messages
import uuid
import razorpay
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
import json
from django.utils import timezone
from .demo_utils import reset_demo_data # Import the helper

@require_http_methods(["GET"])
def product_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.filter(is_active=True).exclude(artisan__username='artisan_demo').select_related('artisan', 'category')
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        products = products.filter(category__slug=category)
    
    categories = Category.objects.all()
    
    recommended_products = []
    if request.user.is_authenticated:
        try:
            # Get categories of products the user has bought
            purchased_categories = OrderItem.objects.filter(
                order__customer=request.user
            ).values_list('product__category', flat=True).distinct()
            
            if purchased_categories:
                recommended_products = Product.objects.filter(
                    is_active=True,
                    category__in=purchased_categories
                ).select_related('artisan', 'category').order_by('?')[:4]
        except Exception:
            # Fail silently for recommendations if there's a data issue
            recommended_products = []

    return render(request, 'store/product_list.html', {
        'products': products, 
        'query': query,
        'categories': categories,
        'recommended_products': recommended_products
    })

def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('artisan').prefetch_related('reviews'), pk=pk)
    reviews = product.reviews.select_related('customer')
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    related_products = Product.objects.filter(is_active=True, category=product.category).exclude(pk=pk)[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products
    }

    # Prefer product_detail.html; fall back to product_detail_v2.html if missing
    template_name = 'store/product_detail.html'
    try:
        get_template(template_name)
    except TemplateDoesNotExist:
        template_name = 'store/product_detail_v2.html'

    return render(request, template_name, context)

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
    # AUTO-RESET for Demo User
    if request.user.username == 'artisan_demo':
        reset_demo_data(request.user)

    # Filter orders that contain products made by this artisan
    pending_orders = Order.objects.filter(
        status='PENDING',
        items__product__artisan=request.user
    ).distinct().prefetch_related('items__product').order_by('created_at') # Sort Oldest First

    active_orders = Order.objects.filter(
        items__product__artisan=request.user
    ).exclude(
        status__in=['PENDING', 'COMPLETED', 'CANCELLED']
    ).distinct().prefetch_related('items__product')

    completed_orders = Order.objects.filter(
        status__in=['COMPLETED', 'CANCELLED'],
        items__product__artisan=request.user
    ).distinct().order_by('-updated_at')[:5]
    
    # Dashboard Stats
    total_orders = Order.objects.filter(items__product__artisan=request.user).distinct().count()
    total_customers = Order.objects.filter(items__product__artisan=request.user).values('customer').distinct().count()
    
    # Calculate Total Revenue (only from items belonging to this artisan)
    revenue_items = OrderItem.objects.filter(
        product__artisan=request.user
    ).exclude(order__status='CANCELLED')
    
    total_revenue = int(sum(item.get_subtotal() for item in revenue_items))

    # Fetch recent chat inquiries
    inquiries = ChatInquiry.objects.all()[:10]  # Show last 10 messages for now

    return render(request, 'store/artisan_dashboard.html', {
        'pending_orders': pending_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'inquiries': inquiries, # Pass inquiries to template
    })

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["POST"])
def start_preparing(request, pk):
    order = get_object_or_404(Order, pk=pk, items__product__artisan=request.user)
    if order.status == 'PENDING':
        order.status = 'IN_PROGRESS'
        OrderUpdate.objects.create(order=order, description="Started preparing your order! 🧶")
        order.save()
        messages.success(request, f"Order #{order.id} moved to In Progress.")
    return redirect('artisan_dashboard')

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_orders(request):
    """View all orders for the artisan"""
    orders = Order.objects.filter(
        items__product__artisan=request.user
    ).distinct().order_by('-created_at')
    
    return render(request, 'store/artisan_orders_list.html', {'orders': orders})

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_stats(request):
    """Dedicated statistics page for artisans"""
    # Helper to get artisan's relevant items/orders
    # We filter orders that contain at least one product from this artisan
    artisan_orders = Order.objects.filter(items__product__artisan=request.user).distinct()

    # Totals for Cards
    total_orders = artisan_orders.count()
    total_customers = artisan_orders.values('customer').distinct().count()
    
    # Revenue: Sum of OrderItems belonging to this artisan only
    revenue_items = OrderItem.objects.filter(product__artisan=request.user).exclude(order__status='CANCELLED')
    total_revenue = int(sum(item.get_subtotal() for item in revenue_items))

    # Chart Data
    pending_count = artisan_orders.filter(status='PENDING').count()
    active_count = artisan_orders.exclude(status__in=['PENDING', 'COMPLETED', 'CANCELLED']).count()
    completed_count = artisan_orders.filter(status__in=['COMPLETED', 'CANCELLED']).count()

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
def artisan_settings(request):
    from users.forms import ArtisanProfileForm
    
    if request.method == 'POST':
        form = ArtisanProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully! ✨')
            return redirect('artisan_settings')
    else:
        form = ArtisanProfileForm(instance=request.user)
    
    return render(request, 'store/artisan_settings.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_artisan)
def download_invoice(request, pk):
    order = get_object_or_404(Order, pk=pk, items__product__artisan=request.user)
    return render(request, 'store/invoice.html', {'order': order})

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_invoices(request):
    orders = Order.objects.filter(items__product__artisan=request.user).distinct().order_by('-created_at')
    return render(request, 'store/artisan_invoices.html', {'orders': orders})

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
    
    # Razorpay bypassed - Direct Checkout
    
    return render(request, 'store/checkout.html', {
        'cart': cart,
        'razorpay_order': None, # explicitly None
        'razorpay_key_id': None,
        'total_amount': total_amount,
        'form': CheckoutForm() # Add empty form
    })

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                cart = Cart.objects.get(user=request.user)
                
                with transaction.atomic():
                    # Create Order with form data
                    order = form.save(commit=False)
                    order.customer = request.user
                    order.status = 'PENDING'
                    
                    # Apply Coupon if present
                    if cart.coupon and cart.coupon.active:
                        order.coupon = cart.coupon
                        order.discount_amount = cart.get_discount_amount()
                        
                    order.save()
                    
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
                messages.error(request, f"Error processing order: {e}")
                return redirect('checkout')
        else:
            messages.error(request, "Please fill in all required shipping details correctly.")
            # In a real app, we'd re-render checkout with errors, but here we redirect for simplicity
            return redirect('checkout')
            
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

def about_us(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Fetch the main artisan 'mansi'
    artisan = User.objects.filter(username='mansi').first()
    return render(request, 'store/about_us.html', {'artisan': artisan})

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_products_list(request):
    """List all products for the artisan with management options"""
    try:
        # Show ONLY products for this artisan
        products = Product.objects.filter(artisan=request.user).select_related('category').order_by('-created_at')
        
        # Search functionality
        query = request.GET.get('q', '')
        if query:
            products = products.filter(name__icontains=query)
            
        return render(request, 'store/artisan_products_list.html', {'products': products, 'query': query})
    except Exception as e:
        messages.error(request, "Error loading your collection. Please try again.")
        return render(request, 'store/artisan_products_list.html', {'products': [], 'query': ''})

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

@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_coupons(request):
    """List and manage coupons"""
    coupons = Coupon.objects.all().order_by('-id')
    return render(request, 'store/artisan_coupons.html', {'coupons': coupons, 'form': CouponForm()})

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["POST"])
def add_coupon(request):
    """Add a new coupon"""
    form = CouponForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "New promo code created! 🎫")
    else:
        messages.error(request, "Error creating coupon. Code might be duplicate.")
    return redirect('artisan_coupons')

@login_required
@user_passes_test(lambda u: u.is_artisan)
@require_http_methods(["POST"])
def delete_coupon(request, pk):
    """Delete a coupon"""
    coupon = get_object_or_404(Coupon, pk=pk)
    coupon.delete()
    messages.success(request, "Coupon deleted.")
    return redirect('artisan_coupons')
@login_required
@require_http_methods(["POST"])
def apply_coupon(request):
    raw_code = request.POST.get('code', '')
    code = raw_code.strip()
    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
        cart = request.user.cart
        cart.coupon = coupon
        cart.save()
        messages.success(request, f"Coupon '{code}' applied! 🏷️")
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid or expired coupon code.")
    
    next_url = request.POST.get('next', 'view_cart')
    return redirect(next_url)

@login_required
def remove_coupon(request):
    cart = request.user.cart
    cart.coupon = None
    cart.save()
    messages.info(request, "Coupon removed.")
    
    next_url = request.GET.get('next', 'view_cart')
    return redirect(next_url)

@login_required
@user_passes_test(lambda u: u.is_artisan)
@login_required
@user_passes_test(lambda u: u.is_artisan)
def artisan_chat_inquiries(request):
    """View and Reply to chat inquiries"""
    if request.method == 'POST':
        inquiry_id = request.POST.get('inquiry_id')
        reply_text = request.POST.get('reply', '').strip()
        
        if inquiry_id and reply_text:
            inquiry = get_object_or_404(ChatInquiry, pk=inquiry_id)
            inquiry.reply = reply_text
            inquiry.replied_at = timezone.now()
            inquiry.replied_by = request.user
            inquiry.is_read = True
            inquiry.save()
            messages.success(request, "Reply sent successfully!")
            return redirect('artisan_chat_inquiries')

    inquiries = ChatInquiry.objects.all()
    
    # AJAX Polling
    if request.GET.get('mode') == 'poll':
         return render(request, 'store/includes/inquiries_list.html', {'inquiries': inquiries})

    return render(request, 'store/artisan_inquiries.html', {'inquiries': inquiries})

@csrf_exempt
@require_http_methods(["POST"])
def save_chat_message(request):
    """API Endpoint to save chat message"""
    try:
        data = json.loads(request.body)
        message_text = data.get('message', '').strip()
        
        if message_text:
            sender = request.user if request.user.is_authenticated else None
            ChatInquiry.objects.create(sender=sender, message=message_text)
            return JsonResponse({'status': 'success', 'message': 'Message sent'})
        
        return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def fetch_chat_history(request):
    """API to fetch history for logged in user"""
    if request.user.is_authenticated:
        messages = ChatInquiry.objects.filter(sender=request.user).order_by('created_at')[:50] # Limit to 50
        data = []
        for msg in messages:
            data.append({
                'id': f"msg_{msg.id}",
                'message': msg.message,
                'created_at': msg.created_at.strftime("%H:%M"),
                'is_user': True
            })
            if msg.reply:
                data.append({
                    'id': f"reply_{msg.id}",
                    'message': msg.reply,
                    'created_at': msg.replied_at.strftime("%H:%M") if msg.replied_at else "",
                    'is_user': False,
                    'sender_name': msg.replied_by.get_display_name() if msg.replied_by else "Support"
                })
        return JsonResponse({'status': 'success', 'messages': data})
    else:
        # TODO: Implement guest logic using session or cookie if needed
        return JsonResponse({'status': 'success', 'messages': []}) # Return empty for guest for now
