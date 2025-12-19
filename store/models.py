from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
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
    image = models.ImageField(upload_to='products/', blank=True, null=True)
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
        ]

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('FINISHING', 'Finishing Touches'),
        ('READY', 'Ready for Shipping'),
        ('SHIPPED', 'Shipped'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    customization_notes = models.TextField(blank=True, help_text="Special requests from the customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
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
        return sum(item.price_at_purchase * item.quantity for item in self.items.all())

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

    class Meta:
        unique_together = ['product', 'customer']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.username} - {self.product.name} ({self.rating}★)"

class Subscriber(models.Model):
    """Newsletter subscriber email list"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
