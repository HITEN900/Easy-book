import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User
from apps.bus_owners.models import Bus, Route, Seat, OwnerBankDetails
from django.utils import timezone

def create_seats(bus, total_seats=40):
    for row in range(1, 11):
        for col in ['A','B','C','D']:
            seat_number = f'{row}{col}'
            seat_type = 'window' if col in ['A','D'] else 'aisle'
            Seat.objects.create(
                bus=bus,
                seat_number=seat_number,
                seat_type=seat_type,
                seat_row=row,
                seat_column=ord(col) - 64,
                is_active=True
            )

# Get admin user
admin = User.objects.get(username='admin')
admin.user_type = 'bus_owner'
admin.save()

# Add bank details
OwnerBankDetails.objects.create(
    owner=admin,
    account_holder_name='Admin Travels',
    bank_name='State Bank of India',
    account_number='12345678901',
    ifsc_code='SBIN0001234',
    upi_id='admin@okhdfcbank'
)

# Create bus
bus = Bus.objects.create(
    owner=admin,
    bus_name='Rajdhani Express',
    bus_type='ac',
    bus_number='RJ1234',
    total_seats=40,
    seat_layout='2x2',
    amenities='AC, WiFi, Charging Point'
)

# Create seats
create_seats(bus)

# Create route
departure = timezone.make_aware(datetime.now() + timedelta(days=2, hours=8))
arrival = timezone.make_aware(datetime.now() + timedelta(days=2, hours=12))

route = Route.objects.create(
    bus=bus,
    source='Mumbai',
    destination='Pune',
    departure_time=departure,
    arrival_time=arrival,
    fare=499,
    operating_days='All Days',
    available_seats=40
)

print("✅ Setup complete!")
print(f"Bus: {bus.bus_name}")
print(f"Route: Mumbai → Pune")
print(f"Date: {departure.strftime('%d %b %Y')}")
print(f"Time: {departure.strftime('%I:%M %p')}")
print(f"Fare: ₹499")