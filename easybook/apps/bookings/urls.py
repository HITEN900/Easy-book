from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_buses, name='search_buses'),
    path('bus/<int:route_id>/', views.bus_details, name='bus_details'),
    path('book/<int:route_id>/', views.book_tickets, name='book_tickets'),
    path('passenger/<int:route_id>/<str:seats>/', views.passenger_details, name='passenger_details'),
    path('payment/<int:booking_id>/', views.payment_options, name='payment_options'),
    path('process-payment/<int:booking_id>/', views.process_payment, name='process_payment'),
    path('payment-failed/<int:booking_id>/', views.payment_failed, name='payment_failed'),
    path('payment-status/<int:booking_id>/', views.check_payment_status, name='payment_status'),
    path('payment-webhook/<int:booking_id>/', views.payment_webhook, name='payment_webhook'),
    path('simulate-upi/<int:booking_id>/', views.simulate_upi_payment, name='simulate_upi'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('download/<int:booking_id>/', views.download_ticket, name='download_ticket'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]