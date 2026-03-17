from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User
from apps.bookings.models import Booking

# Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on user type
            if user.user_type == 'bus_owner':
                return redirect('bus_owner_dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

# Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        user_type = request.POST.get('user_type', 'customer')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'signup.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            user_type=user_type
        )
        
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Account created successfully!')
        
        # Redirect based on user type
        if user_type == 'bus_owner':
            return redirect('bus_owner_dashboard')
        else:
            return redirect('dashboard')
    
    return render(request, 'signup.html')

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# Dashboard View
@login_required
def dashboard(request):
    if request.user.user_type == 'bus_owner':
        return redirect('bus_owner_dashboard')
    else:
        # Get customer's bookings
        bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
        
        # Calculate statistics
        total_bookings = bookings.count()
        upcoming_bookings = bookings.filter(
            status='confirmed', 
            journey_date__gte=timezone.now().date()
        ).count()
        completed_bookings = bookings.filter(status='completed').count()
        cancelled_bookings = bookings.filter(status='cancelled').count()
        
        # Get recent bookings
        recent_bookings = bookings[:5]
        
        context = {
            'bookings': bookings,
            'recent_bookings': recent_bookings,
            'total_bookings': total_bookings,
            'upcoming_bookings': upcoming_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
        }
        return render(request, 'customer/dashboard.html', context)

# Profile View
@login_required
def profile_view(request):
    if request.method == 'POST':
        # Update user profile
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        
        # Check if email already exists for another user
        if email != request.user.email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('profile')
        
        # Check if phone already exists for another user
        if phone != request.user.phone and User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('profile')
        
        # Update user
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.phone = phone
        request.user.address = address
        request.user.city = city
        request.user.state = state
        request.user.pincode = pincode
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    return render(request, 'customer/profile.html', {'user': request.user})

# Change Password View
@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return redirect('change_password')
        
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Password changed successfully! Please login again.')
        return redirect('login')
    
    return render(request, 'customer/change_password.html')
