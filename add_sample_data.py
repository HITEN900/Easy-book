import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User
from apps.bus_owners.models import Bus, Route, Seat
from apps.bus_owners.views import create_seats_for_bus
from django.utils import timezone

# Get or create bus owner
try:
    owner = User.objects.get(username='admin')
    owner.user_type = 'bus_owner'
    owner.save()
    print("✓ Admin user updated to bus owner")
except User.DoesNotExist:
    owner = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        phone='9999999999',
        user_type='bus_owner',
        is_superuser=True,
        is_staff=True
    )
    print("✓ Admin user created as bus owner")

# Delete existing sample data
Bus.objects.filter(owner=owner).delete()
print("✓ Existing buses deleted")

# Create sample buses
sample_buses = [
    {
        'bus_name': 'Express Travels',
        'bus_type': 'ac',
        'bus_number': 'HR55AB1234',
        'total_seats': 40,
        'seat_layout': '2x2',
        'amenities': 'AC, WiFi, Charging Point, TV, Snacks'
    },
    {
        'bus_name': 'Royal Cruiser',
        'bus_type': 'sleeper',
        'bus_number': 'HR55CD5678',
        'total_seats': 30,
        'seat_layout': 'sleeper_2x1',
        'amenities': 'AC, WiFi, Charging Point, Blanket, Water Bottle'
    },
    {
        'bus_name': 'City Connect',
        'bus_type': 'non_ac',
        'bus_number': 'HR55EF9012',
        'total_seats': 50,
        'seat_layout': '2x2',
        'amenities': 'Charging Point, TV'
    }
]

for bus_data in sample_buses:
    bus = Bus.objects.create(
        owner=owner,
        **bus_data
    )
    create_seats_for_bus(bus, bus.seat_layout, bus.total_seats)
    print(f"✓ Bus created: {bus.bus_name} ({bus.bus_number}) with {bus.total_seats} seats")
    
    # Create 2 routes for each bus
    routes = [
        {
            'source': 'Delhi',
            'destination': 'Jaipur',
            'departure': timezone.make_aware(datetime.now() + timedelta(days=1, hours=20)),
            'arrival': timezone.make_aware(datetime.now() + timedelta(days=2, hours=6)),
            'fare': 799
        },
        {
            'source': 'Delhi',
            'destination': 'Agra',
            'departure': timezone.make_aware(datetime.now() + timedelta(days=2, hours=8)),
            'arrival': timezone.make_aware(datetime.now() + timedelta(days=2, hours=12)),
            'fare': 499
        }
    ]
    
    for route_data in routes:
        route = Route.objects.create(
            bus=bus,
            source=route_data['source'],
            destination=route_data['destination'],
            departure_time=route_data['departure'],
            arrival_time=route_data['arrival'],
            fare=route_data['fare'],
            operating_days='All Days',
            available_seats=bus.total_seats
        )
        print(f"  └─ Route added: {route.source} → {route.destination} (₹{route.fare})")

print("\n" + "="*50)
print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
print("="*50)
print(f"Username: admin")
print(f"Password: admin123")
print(f"Total Buses: {Bus.objects.filter(owner=owner).count()}")
print(f"Total Routes: {Route.objects.filter(bus__owner=owner).count()}")
print("="*50)