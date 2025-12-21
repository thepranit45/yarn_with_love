from django import forms
from .models import Product, Order, OrderUpdate, Review, Coupon, Category
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'New Category Name'}),
        }

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'color_name', 'short_description', 'price', 'mrp', 'image', 'key_features', 'care_instructions', 'specifications', 'estimated_days_to_complete', 'is_returnable']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'color_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Color (e.g. Red, Blue)'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Short intro (appears on product page)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Full product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01', 'placeholder': 'MRP (optional)'}),
            'estimated_days_to_complete': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'key_features': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter each feature on a new line'}),
            'care_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter each instruction on a new line'}),
            'specifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. Size: Small, Material: Cotton'}),
            'is_returnable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    extra_images = forms.FileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'multiple': True}),
        required=False,
        label="Gallery Images (Select multiple)"
    )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0.01:
            raise ValidationError("Price must be at least 0.01")
        return price

    def clean_estimated_days_to_complete(self):
        days = self.cleaned_data.get('estimated_days_to_complete')
        if days and days < 1:
            raise ValidationError("Must be at least 1 day")
        return days


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class OrderUpdateForm(forms.ModelForm):
    class Meta:
        model = OrderUpdate
        fields = ['description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share the story of this stitch...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "Yarn a Story (Update)"
        self.fields['image'].label = "Progress Photo"


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i} {'★' * i}") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your feedback...'
            }),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone_number', 'shipping_address', 'landmark', 'city', 'state', 'zip_code', 'customization_notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address (Street, Apt, etc.)'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landmark (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP Code'}),
            'customization_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special requests?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required
        required_fields = ['full_name', 'email', 'phone_number', 'shipping_address', 'city', 'state', 'zip_code']
        for field in required_fields:
            self.fields[field].required = True
        
        # Explicitly make these optional
        self.fields['landmark'].required = False
        self.fields['customization_notes'].required = False

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percentage', 'active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PROMOCODE'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VariantLinkForm(forms.Form):
    variant_product = forms.ModelChoiceField(
        queryset=Product.objects.none(),
        label="Select a product to link as a color variant:",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Choose a product..."
    )

    def __init__(self, *args, **kwargs):
        artisan = kwargs.pop('artisan')
        category = kwargs.pop('category')
        current_product_id = kwargs.pop('current_product_id')
        super().__init__(*args, **kwargs)
        
        # Filter products: Same artisan, same category, exclude itself
        self.fields['variant_product'].queryset = Product.objects.filter(
            artisan=artisan, 
            category=category
        ).exclude(id=current_product_id)
