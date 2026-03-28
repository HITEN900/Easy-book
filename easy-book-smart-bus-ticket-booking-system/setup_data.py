import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User
from apps.bus_owners.models import Bus, Route, Seat, OwnerBankDetails
from django.utils import timezone

def create_seats_for_bus(bus, layout, total_seats):
    """Create seats for a bus"""
    seat_number = 1
    if layout == '2x2':
        rows = (total_seats + 3) // 4
        for row in range(1, rows + 1):
            for col in range(1, 5):
                if seat_number <= total_seats:
                    if col == 1 or col == 4:
                        seat_type = 'window'
                    else:
                        seat_type = 'aisle'
                    
                    Seat.objects.create(
                        bus=bus,
                        seat_number=f'{row}{chr(64+col)}',
                        seat_type=seat_type,
                        seat_row=row,
                        seat_column=col,
                        is_active=True
                    )
                    seat_number += 1
    return seat_number - 1

print("="*60)
print("🚀 EASY BOOK - SETUP SCRIPT")
print("="*60)

# Get admin user
try:
    admin = User.objects.get(username='admin')
    admin.user_type = 'bus_owner'
    admin.save()
    print("✓ Admin user configured as bus owner")
except User.DoesNotExist:
    print("✗ Admin user not found. Please create superuser first.")
    exit()

# Add bank details for admin
bank, created = OwnerBankDetails.objects.get_or_create(
    owner=admin,
    defaults={
        'account_holder_name': 'Admin Travels',
        'bank_name': 'State Bank of India',
        'account_number': '12345678901',
        'ifsc_code': 'SBIN0001234',
        'upi_id': 'admin@okhdfcbank',
        'phonepe_number': '9876543210',
        'googlepay_number': '9876543210',
        'paytm_number': '9876543210'
    }
)
if created:
    print("✓ Bank details added for admin")
else:
    print("✓ Bank details already exist")

# Delete existing buses
Bus.objects.filter(owner=admin).delete()
print("\n✓ Existing buses deleted")

# Create sample buses
buses_data = [
    {
        'name': 'Rajdhani Express',
        'type': 'ac',
        'number': 'RJ1234',
        'seats': 40,
        'layout': '2x2',
        'amenities': 'AC, WiFi, Charging Point, TV, Snacks'
    },
    {
        'name': 'Shatabdi Travels',
        'type': 'ac_sleeper',
        'number': 'ST5678',
        'seats': 30,
        'layout': 'sleeper_2x1',
        'amenities': 'AC, WiFi, Blanket, Pillow'
    },
    {
        'name': 'Ordinary Express',
        'type': 'non_ac',
        'number': 'OE9012',
        'seats': 50,
        'layout': '2x2',
        'amenities': 'Charging Point, Fan'
    },
]

routes_data = [
    {'source': 'Mumbai', 'dest': 'Pune', 'fare': 499},
    {'source': 'Delhi', 'dest': 'Jaipur', 'fare': 799},
    {'source': 'Bangalore', 'dest': 'Mysore', 'fare': 299},
    {'source': 'Chennai', 'dest': 'Pondicherry', 'fare': 399},
]

# Create buses with routes
for i, bus_data in enumerate(buses_data):
    # Create bus
    bus = Bus.objects.create(
        owner=admin,
        bus_name=bus_data['name'],
        bus_type=bus_data['type'],
        bus_number=bus_data['number'],
        total_seats=bus_data['seats'],
        seat_layout=bus_data['layout'],
        amenities=bus_data['amenities'],
        is_active=True
    )
    
    # Create seats
    seats_created = create_seats_for_bus(bus, bus_data['layout'], bus_data['seats'])
    print(f"\n✓ Bus created: {bus.bus_name} ({bus.bus_number}) with {seats_created} seats")
    
    # Create 2 routes for each bus
    for j in range(2):
        route_idx = (i * 2 + j) % len(routes_data)
        route_data = routes_data[route_idx]
        
        # Set departure time
        base_date = datetime.now() + timedelta(days=2)
        departure_naive = datetime(
            base_date.year, base_date.month, base_date.day,
            8 + j*4, 0, 0
        )
        arrival_naive = departure_naive + timedelta(hours=4)
        
        departure = timezone.make_aware(departure_naive)
        arrival = timezone.make_aware(arrival_naive)
        
        route = Route.objects.create(
            bus=bus,
            source=route_data['source'],
            destination=route_data['dest'],
            departure_time=departure,
            arrival_time=arrival,
            fare=route_data['fare'],
            operating_days='All Days',
            available_seats=bus.total_seats
        )
        print(f"  └─ Route: {route.source} → {route.destination} - ₹{route.fare}")
        print(f"     Date: {departure.strftime('%d %b %Y')} at {departure.strftime('%I:%M %p')}")

print("\n" + "="*60)
print("✅ SETUP COMPLETED SUCCESSFULLY!")
print("="*60)
print("\n📊 SUMMARY:")
print(f"• Buses: {Bus.objects.filter(owner=admin).count()}")
print(f"• Routes: {Route.objects.filter(bus__owner=admin).count()}")
print(f"• Seats: {Seat.objects.filter(bus__owner=admin).count()}")

print("\n🔑 LOGIN CREDENTIALS:")
print("-"*40)
print("Admin: admin / admin123")
print("\n📅 AVAILABLE ROUTES FOR TESTING:")
print("-"*40)

routes = Route.objects.filter(bus__owner=admin).order_by('departure_time')[:5]
for route in routes:
    print(f"\n• {route.source} → {route.destination}")
    print(f"  Bus: {route.bus.bus_name}")
    print(f"  Date: {route.departure_time.strftime('%d %b %Y')}")
    print(f"  Time: {route.departure_time.strftime('%I:%M %p')}")
    print(f"  Fare: ₹{route.fare}")

print("\n" + "="*60)
print("🎯 NEXT STEPS:")
print("1. Run: python manage.py runserver")
print("2. Login as admin at http://127.0.0.1:8000/admin/")
print("3. Or create customer account at http://127.0.0.1:8000/accounts/signup/")
print("4. Search for buses using the routes above")
print("="*60)