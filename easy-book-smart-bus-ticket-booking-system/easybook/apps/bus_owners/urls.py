from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.bus_owner_registration, name='bus_owner_registration'),
    path('dashboard/', views.bus_owner_dashboard, name='bus_owner_dashboard'),
    path('add-bus/', views.add_bus, name='add_bus'),
    path('manage-buses/', views.manage_buses, name='manage_buses'),
    path('edit-bus/<int:bus_id>/', views.edit_bus, name='edit_bus'),
    path('delete-bus/<int:bus_id>/', views.delete_bus, name='delete_bus'),
    path('add-route/<int:bus_id>/', views.add_route, name='add_route'),
    path('manage-routes/<int:bus_id>/', views.manage_routes, name='manage_routes'),
    path('edit-route/<int:route_id>/', views.edit_route, name='edit_route'),
    path('delete-route/<int:route_id>/', views.delete_route, name='delete_route'),
    path('seat-layout/<int:bus_id>/', views.bus_seat_layout, name='bus_seat_layout'),
    path('update-seat/<int:seat_id>/', views.update_seat_status, name='update_seat_status'),
    path('bookings/', views.bus_bookings, name='bus_bookings'),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
    path('update-booking/<int:booking_id>/', views.update_booking_status, name='update_booking_status'),
    path('add-stop/<int:route_id>/', views.add_bus_stop, name='add_bus_stop'),
    path('earnings/', views.earnings_report, name='earnings'),
    path('booking-stats/', views.owner_booking_stats, name='owner_booking_stats'),
    path('bank-details/', views.add_bank_details, name='add_bank_details'),
]