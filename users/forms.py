from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'is_artisan', 'bio')

class CustomerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

class ArtisanProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'profile_image', 'vacation_mode', 'payment_qr_code']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Tell us about your craft...'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'payment_qr_code': forms.FileInput(attrs={'class': 'form-control'}),
            'vacation_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentQRForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['payment_qr_code']
        widgets = {
            'payment_qr_code': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

from allauth.socialaccount.forms import SignupForm

class CustomSocialSignupForm(SignupForm):
    phone_number = forms.CharField(
        required=True,
        label='Mobile Number',
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +91 9876543210'})
    )

    def save(self, request):
        # Allow the default save to run first
        user = super(CustomSocialSignupForm, self).save(request)
        
        # Then save our custom field
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Tell us about yourself...'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddArtistForm(UserCreationForm):
    """Form for admins to quick-add an artist"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
