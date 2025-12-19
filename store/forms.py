from django import forms
from .models import Product, Order, OrderUpdate, Review
from django.core.exceptions import ValidationError

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'image', 'estimated_days_to_complete']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
            'estimated_days_to_complete': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

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
