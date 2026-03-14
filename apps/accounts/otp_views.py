from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from .models import User, OTP
import random
import string
from twilio.rest import Client
import requests

def send_otp_via_twilio(phone_number, otp):
    """Send OTP via Twilio SMS"""
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f'Your Easy Book verification code is: {otp}. Valid for 5 minutes.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True, message.sid
    except Exception as e:
        print(f"Twilio error: {e}")
        return False, str(e)

def send_otp_via_api(phone_number, otp):
    """Alternative: Send OTP via third-party SMS API"""
    # Example using Fast2SMS (India)
    url = "https://www.fast2sms.com/dev/bulkV2"
    
    headers = {
        'authorization': "YOUR_API_KEY_HERE",
        'Content-Type': "application/x-www-form-urlencoded",
    }
    
    payload = f"variables_values={otp}&route=otp&numbers={phone_number[1:]}"
    
    try:
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code == 200:
            return True, response.json()
        return False, response.text
    except Exception as e:
        return False, str(e)

def request_otp(request):
    """Request OTP for phone number"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        purpose = request.POST.get('purpose', 'login')
        
        # Validate phone number
        if not phone or len(phone) < 10:
            messages.error(request, 'Please enter a valid phone number')
            return redirect('request_otp')
        
        # Check if user exists for login
        if purpose == 'login' and not User.objects.filter(phone=phone).exists():
            messages.error(request, 'No account found with this phone number')
            return redirect('signup')
        
        # Check if user exists for signup
        if purpose == 'signup' and User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered')
            return redirect('login')
        
        # Generate and save OTP
        otp_obj = OTP.objects.create(
            phone=phone,
            purpose=purpose
        )
        
        # Send OTP via Twilio
        success, result = send_otp_via_twilio(phone, otp_obj.otp)
        
        if success:
            messages.success(request, 'OTP sent successfully!')
            request.session['otp_phone'] = phone
            request.session['otp_purpose'] = purpose
            return redirect('verify_otp')
        else:
            messages.error(request, 'Failed to send OTP. Please try again.')
            return redirect('request_otp')
    
    return render(request, 'accounts/request_otp.html')

def verify_otp(request):
    """Verify OTP and login/register user"""
    if request.method == 'POST':
        otp = request.POST.get('otp')
        phone = request.session.get('otp_phone')
        purpose = request.session.get('otp_purpose')
        
        if not phone or not purpose:
            messages.error(request, 'Session expired. Please request OTP again.')
            return redirect('request_otp')
        
        try:
            otp_obj = OTP.objects.filter(
                phone=phone, 
                otp=otp, 
                is_verified=False
            ).latest('created_at')
            
            if otp_obj.is_valid():
                # Mark OTP as verified
                otp_obj.is_verified = True
                otp_obj.save()
                
                if purpose == 'signup':
                    # Create new user
                    return redirect('complete_signup')
                else:
                    # Login existing user
                    user = User.objects.get(phone=phone)
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    
                    # Clear session
                    del request.session['otp_phone']
                    del request.session['otp_purpose']
                    
                    return redirect('dashboard')
            else:
                messages.error(request, 'OTP has expired. Please request again.')
                
        except OTP.DoesNotExist:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'accounts/verify_otp.html')

def complete_signup(request):
    """Complete signup after OTP verification"""
    phone = request.session.get('otp_phone')
    
    if not phone:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('signup')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type', 'customer')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone=phone,
            user_type=user_type,
            phone_verified=True
        )
        
        login(request, user)
        messages.success(request, 'Account created successfully!')
        
        # Clear session
        del request.session['otp_phone']
        del request.session['otp_purpose']
        
        return redirect('dashboard')
    
    return render(request, 'accounts/complete_signup.html', {'phone': phone})