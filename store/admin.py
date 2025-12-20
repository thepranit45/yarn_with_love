from django.contrib import admin
from .models import Category, Product, Order, OrderItem, OrderUpdate, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderUpdateInline(admin.TabularInline):
    model = OrderUpdate
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at', 'tracking_id']
    list_filter = ['status', 'created_at']
    inlines = [OrderItemInline, OrderUpdateInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'artisan', 'price', 'category', 'created_at']
    list_filter = ['category', 'artisan']

admin.site.register(Category)
admin.site.register(OrderUpdate) # Optional, can be managed via Order inline
admin.site.register(Coupon)
