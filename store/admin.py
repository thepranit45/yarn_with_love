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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'
admin.site.register(OrderUpdate) # Optional, can be managed via Order inline
admin.site.register(Coupon)
