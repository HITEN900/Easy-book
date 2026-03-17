from django.urls import path
from . import views

app_name = 'accounts'  # THIS LINE MUST BE HERE

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('bus-owner/dashboard/', views.bus_owner_dashboard, name='bus_owner_dashboard'),
]