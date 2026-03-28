app_name = 'bus_owners'

from django.urls import path
from . import views

urlpatterns = [
    # Registration
    path('register/', views.register, name='register'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Bus Management
    path('add-bus/', views.add_bus, name='add_bus'),
    path('manage-buses/', views.manage_buses, name='manage_buses'),
    path('edit-bus/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('delete-bus/<int:bus_id>/', views.delete_bus, name='delete_bus'),

    # Route Management
    path('manage-routes/<int:bus_id>/', views.manage_routes, name='manage_routes'),
    path('add-route/<int:bus_id>/', views.add_route, name='add_route'),
    path('edit-route/<int:route_id>/', views.edit_route, name='edit_route'),
    path('delete-route/<int:route_id>/', views.delete_route, name='delete_route'),

    # Seat Management
    path('seat-layout/<int:bus_id>/', views.bus_seat_layout, name='bus_seat_layout'),
    path('update-seats/<int:bus_id>/', views.update_seat_layout, name='update_seat_layout'),

    # Bookings & Earnings
    path('bookings/', views.bus_bookings, name='bus_bookings'),
    path('booking-details/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('earnings/', views.earnings, name='earnings'),
    path('booking-stats/', views.owner_booking_stats, name='owner_booking_stats'),

    # Bank Details
    path('bank-details/', views.add_bank_details, name='add_bank_details'),
    path('update-bank-details/', views.update_bank_details, name='update_bank_details'),

    # Profile
    path('profile/', views.owner_profile, name='owner_profile'),
    path('update-profile/', views.update_owner_profile, name='update_owner_profile'),
]