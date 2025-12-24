from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    artisan = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Maximum Retail Price (for discount display)")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    
    # Variant Fields
    color_name = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. Red, Blue, Pastel Pink")
    variant_group = models.UUIDField(default=uuid.uuid4, editable=False, help_text="Products sharing this ID are variants of the same item")
    
    short_description = models.TextField(blank=True, help_text="Short intro for the product page")
    key_features = models.TextField(blank=True, help_text="Enter each feature on a new line")
    care_instructions = models.TextField(blank=True, help_text="Enter each instruction on a new line")
    specifications = models.TextField(blank=True, help_text="Comma-separated specs (e.g. 'Size: Small, Material: Cotton')")
    is_returnable = models.BooleanField(default=False, help_text="Is this item eligible for return?")
    estimated_days_to_complete = models.PositiveIntegerField(default=7, validators=[MinValueValidator(1)], help_text="Estimated days to make this item")
    is_active = models.BooleanField(default=True, help_text="Uncheck to hide this product")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['artisan', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['variant_group']),
        ]

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAYMENT_REVIEW', 'Payment Verification Pending'),
        ('PAYMENT_VERIFIED', 'Payment Verified/Received'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHING', 'Finishing Touches'),
        ('READY', 'Ready for Shipping'),
        ('SHIPPED', 'Shipped'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Shipping Details
    full_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True)
    landmark = models.CharField(max_length=200, blank=True, help_text="Nearby landmark (Optional)")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    
    # Payment Details
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)
    payment_timestamp = models.DateTimeField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    customization_notes = models.TextField(blank=True, help_text="Special requests from the customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['tracking_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} ({self.get_status_display()})"

    def get_total_price(self):
        """Calculate total order price"""
        total = sum(item.price_at_purchase * item.quantity for item in self.items.all())
        return total - self.discount_amount

    def get_progress_percentage(self):
        """Get progress as percentage"""
        status_weights = {
            'PENDING': 10,
            'IN_PROGRESS': 40,
            'FINISHING': 70,
            'READY': 90,
            'SHIPPED': 95,
            'COMPLETED': 100,
            'CANCELLED': 0
        }
        return status_weights.get(self.status, 0)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Don't delete order history if product is deleted
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)], help_text="Price of the product at the time of purchase")

    class Meta:
        unique_together = ['order', 'product']
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        """Calculate subtotal for this item"""
        return self.price_at_purchase * self.quantity

class OrderUpdate(models.Model):
    """
    Represents a 'Story' update from the artisan about the order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='updates')
    description = models.TextField(help_text="The story or update message")
    image = models.ImageField(upload_to='order_updates/', blank=True, null=True, help_text="Photo of the progress")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', '-created_at']),
        ]

    def __str__(self):
        return f"Update for Order #{self.order.id} at {self.created_at}"


class Review(models.Model):
    """Product reviews from customers"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Manual Review Fields (for Artisans to add external reviews)
    customer_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of customer (if added manually)")
    customer_photo = models.ImageField(upload_to='review_photos/', blank=True, null=True)

    class Meta:
        # Remove unique_together because an artisan might add multiple reviews for different manual customers on the same product
        # unique_together = ['product', 'customer'] 
        ordering = ['-created_at']

    def __str__(self):
        name = self.customer_name if self.customer_name else self.customer.username
        return f"{name} - {self.product.name} ({self.rating}★)"

class Subscriber(models.Model):
    """Newsletter subscriber email list"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percentage}%)"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_subtotal(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_total_price(self):
        total = self.get_subtotal()
        if self.coupon and self.coupon.active:
            discount = (total * self.coupon.discount_percentage) / 100
            return int(total - discount)
        return total
    
    def get_discount_amount(self):
        if self.coupon and self.coupon.active:
            total = self.get_subtotal()
            return int((total * self.coupon.discount_percentage) / 100)
        return 0
    
    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    customization_notes = models.TextField(blank=True, help_text="Special requests for this item")
    
    class Meta:
        unique_together = ['cart', 'product']

    def get_subtotal(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.cart.user.username})"


class ChatInquiry(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', '-created_at']),
        ]

    def __str__(self):
        return f"Inquiry by {self.sender.username} at {self.created_at}"
