from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomerRegistrationForm, ProfileForm, AddArtistForm
from .models import CustomUser, ArtisanAccessCode
from django.contrib.auth.decorators import user_passes_test

def register(request):
    """Register as a customer"""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_artisan = False
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('product_list')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

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

def quick_artist_login(request, username):
    """Specific login page for artists (mansi/pranit)"""
    context = {
        'artist_username': username,
        'artist_display': username.capitalize(),
    }
    
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        # If standard authentication fails, check for access codes
        if user is None:
            try:
                # Find the user first
                target_user = CustomUser.objects.get(username=username, is_artisan=True)
                # Check if the password matches any access code for this user
                if ArtisanAccessCode.objects.filter(artisan=target_user, code=password).exists():
                    user = target_user
            except CustomUser.DoesNotExist:
                user = None

        if user is not None:
            if user.is_artisan:
                # Specify backend manually if we bypassed authenticate()
                if not hasattr(user, 'backend'):
                     user.backend = 'django.contrib.auth.backends.ModelBackend'
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_display_name()}! 🧶')
                return redirect('artisan_dashboard')
            else:
                messages.error(request, 'This account is not an artisan account.')
        else:
            messages.error(request, 'Invalid password. Please try again.')
    
    return render(request, 'users/artist_quick_login.html', context)

@login_required
def manage_access_codes(request):
    """View for Pranit to manage access codes for demo accounts"""
    # Only allow Pranit (or superusers) to access
    if request.user.username != 'pranit' and not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('artisan_dashboard')

    # Get the demo artisan user
    try:
        demo_artisan = CustomUser.objects.get(username='artisan_demo')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Demo artisan user not found.')
        return redirect('artisan_dashboard')

    if request.method == 'POST':
        if 'add_code' in request.POST:
            new_code = request.POST.get('new_code')
            desc = request.POST.get('description', '')
            if new_code:
                ArtisanAccessCode.objects.create(
                    artisan=demo_artisan, 
                    code=new_code,
                    description=desc
                )
                messages.success(request, f'Added access code: {new_code}')
        elif 'delete_code' in request.POST:
            code_id = request.POST.get('code_id')
            ArtisanAccessCode.objects.filter(id=code_id).delete()
            messages.success(request, 'Access code removed.')
            
        return redirect('manage_access_codes')

    access_codes = ArtisanAccessCode.objects.filter(artisan=demo_artisan).order_by('-created_at')
    
    return render(request, 'users/manage_access_codes.html', {
        'access_codes': access_codes,
        'demo_artisan': demo_artisan
    })

from store.models import Order

@login_required
def profile(request):
    """User Profile View"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated! ✨')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    # Fetch recent orders (last 5)
    recent_orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]
    
    return render(request, 'users/profile.html', {
        'form': form,
        'recent_orders': recent_orders
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_artisans(request):
    """Admin Dashboard to Manage Artisans"""
    if request.method == 'POST':
        if 'add_artist' in request.POST:
            form = AddArtistForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_artisan = True
                user.save()
                messages.success(request, f"New Artist '{user.username}' created successfully! 🎨")
                return redirect('manage_artisans')
            else:
                messages.error(request, "Error creating artist. Please check the form.")
        elif 'toggle_status' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, pk=user_id)
            if user != request.user: # Prevent admin from disabling themselves
                user.is_artisan = not user.is_artisan
                user.save()
                status = "promoted to Artisan" if user.is_artisan else "demoted to Customer"
                messages.success(request, f"{user.username} has been {status}.")
            return redirect('manage_artisans')
        elif 'reset_password' in request.POST:
            user_id = request.POST.get('user_id')
            new_password = request.POST.get('new_password')
            if user_id and new_password:
                try:
                    user = CustomUser.objects.get(pk=user_id)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, f"Password updated for {user.username} 🔐")
                except CustomUser.DoesNotExist:
                    messages.error(request, "User not found.")
            return redirect('manage_artisans')
    else:
        form = AddArtistForm()

    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_artisans.html', {'users': users, 'form': form})
