from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomerRegistrationForm
from .models import CustomUser

def register(request):
    """Register as a customer"""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_artisan = False
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('product_list')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def register_artist(request):
    """Register as an artisan"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_artisan = True
            user.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! Your artisan account has been created.')
            return redirect('artisan_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register_artist.html', {'form': form})

def login_choice(request):
    """Choose login type: Customer, Artist, or Admin"""
    return render(request, 'users/login_choice.html')

def login_artist(request):
    """Login for artists"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_artisan:
                    login(request, user)
                    messages.success(request, f'Welcome back, {username}!')
                    return redirect('artisan_dashboard')
                else:
                    messages.error(request, 'This account is not an artisan account. Please log in as a customer.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login_artist.html', {'form': form})

def login_admin(request):
    """Login for admin"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff and user.is_superuser:
                    login(request, user)
                    messages.success(request, f'Welcome back, Admin {username}!')
                    return redirect('admin:index')
                else:
                    messages.error(request, 'This account does not have admin privileges.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login_admin.html', {'form': form})

def quick_artist_login(request, username, password):
    """Quick login for artists with pre-set credentials - shows confirmation form"""
    # Show a confirmation page for the artist
    context = {
        'artist_username': username,
        'artist_display': username.capitalize(),
        'quick_login': True
    }
    
    if request.method == 'POST':
        # User confirmed - authenticate and login
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_artisan:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_display_name()}! 🧶')
                return redirect('artisan_dashboard')
            else:
                messages.error(request, 'This account is not an artisan account.')
                return redirect('login_artist')
        else:
            messages.error(request, 'Authentication failed. Please try again.')
            return redirect('login_artist')
    
    # Show confirmation page
    return render(request, 'users/artist_quick_login.html', context)
