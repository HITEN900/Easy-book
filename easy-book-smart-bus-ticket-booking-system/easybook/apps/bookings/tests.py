# from django.test import TestCase

# # Create your tests here.


from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from apps.accounts.models import User
from apps.bus_owners.models import Bus, Route, Seat
from .models import Booking, BookedSeat, Payment


def make_user(username='testuser', user_type='customer'):
    return User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='StrongPass123!',
        phone=f'9{"".join(str(ord(c)) for c in username)[:9]}',
        user_type=user_type,
    )


def make_bus_and_route(owner):
    bus = Bus.objects.create(
        owner=owner, bus_name='TestBus', bus_type='ac',
        bus_number='TN01AB1234', total_seats=10, seat_layout='2x2'
    )
    departure = timezone.now() + timedelta(days=3)
    route = Route.objects.create(
        bus=bus, source='Chennai', destination='Bangalore',
        departure_time=departure,
        arrival_time=departure + timedelta(hours=5),
        fare=500, available_seats=10
    )
    Seat.objects.create(bus=bus, seat_number='1A', seat_type='window',
                        seat_row=1, seat_column=1)
    return bus, route


class BookedSeatMaskingTest(TestCase):
    """FIX: Verify Aadhaar is never stored in full."""

    def setUp(self):
        self.owner = make_user('owner', 'bus_owner')
        self.customer = make_user('customer', 'customer')
        self.bus, self.route = make_bus_and_route(self.owner)
        self.booking = Booking.objects.create(
            user=self.customer, route=self.route,
            journey_date=date.today() + timedelta(days=3),
            total_amount=500, booking_reference='BK1234567890'
        )
        self.seat = Seat.objects.first()

    def test_aadhaar_only_last4_stored(self):
        bs = BookedSeat(booking=self.booking, seat=self.seat,
                        passenger_name='Test', passenger_age=25, passenger_gender='M')
        bs.set_adhar('123456789012')
        bs.save()
        self.assertEqual(bs.passenger_adhar_last4, '9012')
        self.assertEqual(bs.get_masked_adhar(), 'XXXX-XXXX-9012')

    def test_no_aadhaar_handled(self):
        bs = BookedSeat(booking=self.booking, seat=self.seat,
                        passenger_name='Test', passenger_age=25, passenger_gender='M')
        bs.set_adhar('')
        bs.save()
        self.assertIsNone(bs.passenger_adhar_last4)
        self.assertEqual(bs.get_masked_adhar(), 'Not provided')


class SearchBusesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user('owner2', 'bus_owner')
        self.bus, self.route = make_bus_and_route(self.owner)

    def test_search_returns_results(self):
        journey = (timezone.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        resp = self.client.get(reverse('search_buses'), {
            'from': 'Chennai', 'to': 'Bangalore', 'date': journey
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.route, resp.context['routes'])

    def test_invalid_date_does_not_crash(self):
        resp = self.client.get(reverse('search_buses'), {
            'from': 'Chennai', 'to': 'Bangalore', 'date': 'not-a-date'
        })
        self.assertEqual(resp.status_code, 200)


class BookingReferenceUniquenessTest(TestCase):
    """FIX: Confirm booking references are generated with enough entropy."""

    def test_references_are_unique(self):
        from apps.bookings.views import generate_booking_reference
        refs = {generate_booking_reference() for _ in range(1000)}
        # All 1000 should be unique
        self.assertEqual(len(refs), 1000)

    def test_reference_format(self):
        from apps.bookings.views import generate_booking_reference
        ref = generate_booking_reference()
        self.assertTrue(ref.startswith('BK'))
        self.assertEqual(len(ref), 12)  # 'BK' + 10 digits


class CancelBookingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.owner = make_user('owner3', 'bus_owner')
        self.customer = make_user('customer3', 'customer')
        self.bus, self.route = make_bus_and_route(self.owner)
        self.booking = Booking.objects.create(
            user=self.customer, route=self.route,
            journey_date=date.today() + timedelta(days=3),
            total_amount=500, booking_reference='BK9999999999',
            status='confirmed'
        )
        self.client.login(username='customer3', password='StrongPass123!')

    def test_cannot_cancel_within_2_hours(self):
        # Set departure to 1 hour from now
        self.route.departure_time = timezone.now() + timedelta(hours=1)
        self.route.save()
        resp = self.client.post(reverse('cancel_booking', args=[self.booking.id]),
                                {'reason_choice': 'changed_plans'})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'confirmed')  # Should NOT be cancelled

    def test_can_cancel_with_enough_notice(self):
        resp = self.client.post(reverse('cancel_booking', args=[self.booking.id]),
                                {'reason_choice': 'changed_plans'})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        self.assertEqual(self.booking.cancellation_reason, 'changed_plans')