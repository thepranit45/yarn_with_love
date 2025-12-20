from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomerRegistrationForm
from .models import CustomUser, ArtisanAccessCode

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
        elif 'update_status' in request.POST:
            code_id = request.POST.get('code_id')
            new_status = request.POST.get('new_status')
            try:
                code_obj = ArtisanAccessCode.objects.get(id=code_id)
                code_obj.status = new_status
                code_obj.save()
                messages.success(request, 'Status updated.')
            except ArtisanAccessCode.DoesNotExist:
                messages.error(request, 'Code not found.')
            
        return redirect('manage_access_codes')

    access_codes = ArtisanAccessCode.objects.filter(artisan=demo_artisan).order_by('-created_at')
    
    return render(request, 'users/manage_access_codes.html', {
        'access_codes': access_codes,
        'demo_artisan': demo_artisan
    })
