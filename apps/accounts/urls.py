from django.urls import path
from . import views
from . import otp_views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # OTP URLs
    path('request-otp/', otp_views.request_otp, name='request_otp'),
    path('verify-otp/', otp_views.verify_otp, name='verify_otp'),
    path('complete-signup/', otp_views.complete_signup, name='complete_signup'),
]