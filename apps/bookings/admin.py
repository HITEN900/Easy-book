from django.contrib import admin
from .models import Booking, BookedSeat

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'user', 'route', 'journey_date', 'total_amount', 'status']
    list_filter = ['status', 'journey_date']
    search_fields = ['booking_reference', 'user__username']

@admin.register(BookedSeat)
class BookedSeatAdmin(admin.ModelAdmin):
    list_display = ['booking', 'seat', 'passenger_name']