from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.bus_owners.models import Bus, Route, Seat, OwnerBankDetails
from .models import Booking, BookedSeat, Payment
import random
import string
import time
from datetime import datetime
from utils.pdf_generator import generate_ticket_pdf

# Helper functions
def generate_booking_reference():
    return 'BK' + ''.join(random.choices(string.digits, k=8))

def generate_transaction_id():
    return 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

# Search Buses
def search_buses(request):
    if request.method == 'GET':
        source = request.GET.get('from')
        destination = request.GET.get('to')
        journey_date = request.GET.get('date')

        if source and destination and journey_date:
            try:
                journey_date_obj = datetime.strptime(journey_date, '%Y-%m-%d').date()
                routes = Route.objects.filter(
                    source__icontains=source,
                    destination__icontains=destination,
                    departure_time__date=journey_date_obj,
                    available_seats__gt=0
                ).select_related('bus').order_by('departure_time')

                context = {
                    'routes': routes,
                    'source': source,
                    'destination': destination,
                    'journey_date': journey_date,
                    'search_performed': True
                }
                return render(request, 'customer/search_results.html', context)
            except:
                pass

    return render(request, 'customer/search_results.html')


# Bus Details with Seat Layout
@login_required
def bus_details(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    bus = route.bus

    if route.available_seats <= 0:
        messages.error(request, 'No seats available on this bus.')
        return redirect('search_buses')

    seats = Seat.objects.filter(bus=bus).order_by('seat_row', 'seat_column')

    # Get booked seats
    booked_seats = BookedSeat.objects.filter(
        booking__route=route,
        booking__journey_date=route.departure_time.date(),
        booking__status__in=['confirmed', 'pending']
    ).values_list('seat_id', flat=True)

    # Organize seats by row
    seat_rows = {}
    for seat in seats:
        if seat.seat_row not in seat_rows:
            seat_rows[seat.seat_row] = []
        seat.is_booked = seat.id in booked_seats
        seat_rows[seat.seat_row].append(seat)

    context = {
        'route': route,
        'bus': bus,
        'seat_rows': dict(sorted(seat_rows.items())),
        'total_seats': bus.total_seats,
        'available_seats': route.available_seats,
        'booked_seats_count': booked_seats.count()
    }
    return render(request, 'customer/bus_details.html', context)


# Book Tickets
@login_required
def book_tickets(request, route_id):
    route = get_object_or_404(Route, id=route_id)

    if request.method == 'POST':
        selected_seats = request.POST.getlist('seats')
        
        print(f"DEBUG - Selected seats from form: {selected_seats}")

        if not selected_seats:
            messages.error(request, 'Please select at least one seat.')
            return redirect('bus_details', route_id=route_id)

        # Check if seats are still available
        for seat_id in selected_seats:
            if BookedSeat.objects.filter(
                seat_id=seat_id,
                booking__route=route,
                booking__journey_date=route.departure_time.date(),
                booking__status__in=['confirmed', 'pending']
            ).exists():
                messages.error(request, 'Some seats are already booked. Please try again.')
                return redirect('bus_details', route_id=route_id)

        # Convert seats to string for URL parameter
        seats_param = ','.join(str(s) for s in selected_seats)
        print(f"DEBUG - Seats param: {seats_param}")
        
        # Redirect to passenger_details with seats in URL
        return redirect('passenger_details', route_id=route_id, seats=seats_param)

    return redirect('bus_details', route_id=route_id)


# Passenger Details Page
@login_required
def passenger_details(request, route_id, seats):
    route = get_object_or_404(Route, id=route_id)
    
    print(f"DEBUG - Raw seats from URL: {seats}")
    
    # Get seats from URL parameter and ensure they are unique
    if seats:
        selected_seats = list(set(seats.split(',')))  # Use set to remove duplicates
    else:
        selected_seats = []
    
    print(f"DEBUG - Selected seats after processing: {selected_seats}")
    
    # Calculate values directly from the seats parameter
    seat_count = len(selected_seats)
    fare = float(route.fare)
    total_amount = seat_count * fare
    
    print(f"DEBUG - Seat count: {seat_count}")
    print(f"DEBUG - Total amount: {total_amount}")
    
    if seat_count == 0:
        messages.error(request, 'Please select seats first.')
        return redirect('bus_details', route_id=route_id)
    
    # Get seat objects
    seats_objects = Seat.objects.filter(id__in=selected_seats)
    
    if request.method == 'POST':
        passenger_names = request.POST.getlist('passenger_name[]')
        passenger_ages = request.POST.getlist('passenger_age[]')
        passenger_genders = request.POST.getlist('passenger_gender[]')
        passenger_adhar = request.POST.getlist('passenger_adhar[]')

        print(f"DEBUG - Received names count: {len(passenger_names)}")
        print(f"DEBUG - Expected seat count: {seat_count}")

        if len(passenger_names) != seat_count:
            messages.error(request, f'Please fill details for {seat_count} seat(s).')
            return render(request, 'customer/passenger_details.html', {
                'route': route,
                'seats': seats_objects,
                'seat_count': seat_count,
                'total_amount': total_amount,
                'fare_per_seat': fare
            })

        # Validate each passenger's fields
        for i in range(seat_count):
            if not passenger_names[i] or not passenger_names[i].strip():
                messages.error(request, f'Please enter name for seat {i + 1}')
                return render(request, 'customer/passenger_details.html', {
                    'route': route,
                    'seats': seats_objects,
                    'seat_count': seat_count,
                    'total_amount': total_amount,
                    'fare_per_seat': fare
                })

            if not passenger_ages[i] or not passenger_ages[i].strip():
                messages.error(request, f'Please enter age for seat {i + 1}')
                return render(request, 'customer/passenger_details.html', {
                    'route': route,
                    'seats': seats_objects,
                    'seat_count': seat_count,
                    'total_amount': total_amount,
                    'fare_per_seat': fare
                })

            if not passenger_genders[i] or not passenger_genders[i].strip():
                messages.error(request, f'Please select gender for seat {i + 1}')
                return render(request, 'customer/passenger_details.html', {
                    'route': route,
                    'seats': seats_objects,
                    'seat_count': seat_count,
                    'total_amount': total_amount,
                    'fare_per_seat': fare
                })

        try:
            # Final seat availability check
            for seat_id in selected_seats:
                if BookedSeat.objects.filter(
                    seat_id=seat_id,
                    booking__route=route,
                    booking__journey_date=route.departure_time.date(),
                    booking__status__in=['confirmed', 'pending']
                ).exists():
                    messages.error(request, 'Some seats were just booked. Please try again.')
                    return redirect('bus_details', route_id=route_id)

            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                route=route,
                journey_date=route.departure_time.date(),
                total_amount=total_amount,
                status='pending',
                booking_reference=generate_booking_reference()
            )

            # Create booked seats
            for i in range(seat_count):
                seat = Seat.objects.get(id=selected_seats[i])
                adhar = passenger_adhar[i] if i < len(passenger_adhar) and passenger_adhar[i] else ''

                BookedSeat.objects.create(
                    booking=booking,
                    seat=seat,
                    passenger_name=passenger_names[i],
                    passenger_age=int(passenger_ages[i]),
                    passenger_gender=passenger_genders[i],
                    passenger_adhar=adhar
                )

            # Update available seats
            route.available_seats -= seat_count
            route.save()

            messages.success(request, 'Booking created successfully! Proceed to payment.')
            return redirect('payment_options', booking_id=booking.id)

        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('bus_details', route_id=route_id)

    context = {
        'route': route,
        'seats': seats_objects,
        'seat_count': seat_count,
        'total_amount': total_amount,
        'fare_per_seat': fare
    }
    return render(request, 'customer/passenger_details.html', context)


# Payment Options Page
@login_required
def payment_options(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booked_seats = booking.booked_seats.all()

    try:
        owner_bank = OwnerBankDetails.objects.get(owner=booking.route.bus.owner)
    except OwnerBankDetails.DoesNotExist:
        owner_bank = None

    context = {
        'booking': booking,
        'booked_seats': booked_seats,
        'total_amount': booking.total_amount,
        'owner_bank': owner_bank,
        'route': booking.route  # Add route for the template
    }
    return render(request, 'customer/payment_options.html', context)


# ==================== PAYMENT PROCESSING FUNCTIONS ====================

# Process Payment - WORKING VERSION
@login_required
def process_payment(request, booking_id):
    """
    Process payment and confirm booking
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if booking is already confirmed
    if booking.status == 'confirmed':
        messages.success(request, 'Your ticket is already confirmed!')
        return redirect('booking_confirmation', booking_id=booking.id)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Validate payment method
        if not payment_method:
            messages.error(request, 'Please select a payment method.')
            return redirect('payment_options', booking_id=booking.id)

        # Check if payment already exists
        if Payment.objects.filter(booking=booking).exists():
            messages.warning(request, 'Payment already processed.')
            return redirect('booking_confirmation', booking_id=booking.id)

        try:
            # Generate transaction ID
            transaction_id = generate_transaction_id()
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status='success'
            )

            # Update booking
            booking.status = 'confirmed'
            booking.payment_id = transaction_id
            booking.payment_method = payment_method
            booking.save()

            messages.success(request, 'Payment successful! Your ticket is confirmed.')
            return redirect('booking_confirmation', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
            return redirect('payment_options', booking_id=booking.id)

    return redirect('payment_options', booking_id=booking.id)
# Payment Failed Handler - Release seats if payment fails or times out
@login_required
def payment_failed(request, booking_id):
    """
    Handle payment failures and timeouts - releases the booked seats
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Only release seats if booking is still pending
    if booking.status == 'pending':
        # Release the seats
        route = booking.route
        route.available_seats += booking.booked_seats.count()
        route.save()
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()
        
        messages.error(request, 'Payment failed or timed out. Your seats have been released.')
    else:
        messages.info(request, 'This booking cannot be cancelled.')
    
    return redirect('bus_details', route_id=booking.route.id)


# API endpoint for real-time payment status check
@login_required
def check_payment_status(request, booking_id):
    """
    API endpoint to check payment status in real-time
    Used by the frontend to detect successful payments
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Get payment if exists
    payment = Payment.objects.filter(booking=booking).first()
    
    return JsonResponse({
        'status': booking.status,
        'confirmed': booking.status == 'confirmed',
        'payment_status': payment.status if payment else None,
        'booking_reference': booking.booking_reference,
        'transaction_id': payment.transaction_id if payment else None,
        'amount': str(booking.total_amount) if booking.total_amount else None
    })


# WebSocket endpoint simulation (for real-time updates)
@csrf_exempt
@login_required
def payment_webhook(request, booking_id):
    """
    Simulate payment gateway webhook
    In production, this would be called by the payment gateway
    """
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Get payment data from webhook
        transaction_id = request.POST.get('transaction_id', generate_transaction_id())
        payment_status = request.POST.get('status', 'success')
        
        if payment_status == 'success':
            # Create payment record
            Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method='webhook',
                transaction_id=transaction_id,
                status='success'
            )
            
            # Update booking
            booking.status = 'confirmed'
            booking.payment_id = transaction_id
            booking.payment_method = 'webhook'
            booking.save()
            
            return JsonResponse({'status': 'success', 'message': 'Payment confirmed'})
        else:
            return JsonResponse({'status': 'failed', 'message': 'Payment failed'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# Simulate UPI payment detection
@login_required
def simulate_upi_payment(request, booking_id):
    """
    Simulate UPI payment detection for demo purposes
    This would be replaced by actual UPI webhook in production
    """
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        
        # Only process if booking is pending
        if booking.status == 'pending':
            transaction_id = generate_transaction_id()
            
            # Create payment
            Payment.objects.create(
                booking=booking,
                amount=booking.total_amount,
                payment_method='upi',
                transaction_id=transaction_id,
                status='success',
                upi_transaction_id=f'UPI{random.randint(1000000000, 9999999999)}'
            )
            
            # Update booking
            booking.status = 'confirmed'
            booking.payment_id = transaction_id
            booking.payment_method = 'upi'
            booking.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Payment detected and confirmed',
                'redirect_url': reverse('booking_confirmation', args=[booking.id])
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Booking is not in pending state'
            })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# ==================== END OF PAYMENT FUNCTIONS ====================


# Booking Confirmation
@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booked_seats = booking.booked_seats.all()

    context = {
        'booking': booking,
        'booked_seats': booked_seats,
        'route': booking.route,
        'bus': booking.route.bus
    }
    return render(request, 'customer/booking_confirmation.html', context)


# My Bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')

    context = {
        'bookings': bookings
    }
    return render(request, 'customer/my_bookings.html', context)


# Cancel Booking
# @login_required
# def cancel_booking(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, user=request.user)

#     if booking.status in ['confirmed', 'pending']:
#         route = booking.route
#         route.available_seats += booking.booked_seats.count()
#         route.save()

#         booking.status = 'cancelled'
#         booking.save()

#         messages.success(request, 'Booking cancelled successfully.')
#     else:
#         messages.error(request, 'This booking cannot be cancelled.')

#     return redirect('my_bookings')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(
        user=request.user
    ).select_related('route', 'route__bus').prefetch_related('booked_seats__seat').order_by('-booking_date')

    return render(request, 'customer/my_bookings.html', {'bookings': bookings})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status != 'cancelled':
        messages.error(request, 'Only cancelled bookings can be deleted.')
        return redirect('my_bookings')
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted from your history.')
    return redirect('my_bookings')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status not in ['confirmed', 'pending']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('my_bookings')

    if request.method == 'POST':
        reason_choice = request.POST.get('reason_choice', '')
        custom_reason = request.POST.get('custom_reason', '').strip()
        final_reason = custom_reason if reason_choice == 'other' and custom_reason else reason_choice

        route = booking.route
        route.available_seats += booking.booked_seats.count()
        route.save()

        booking.status = 'cancelled'
        # Save reason if your model has the field, otherwise remove next line
        # booking.cancellation_reason = final_reason
        booking.save()

        messages.success(
            request,
            f'Booking #{booking.booking_reference} cancelled. '
            f'Refund of ₹{booking.total_amount} will be credited to your original payment method within 5–7 business days.'
        )
        return redirect('my_bookings')

    return redirect('my_bookings')


# Download Ticket PDF
@login_required
def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booked_seats = booking.booked_seats.all()
    
    # Generate PDF
    pdf = generate_ticket_pdf(
        booking=booking,
        booked_seats=booked_seats,
        route=booking.route,
        bus=booking.route.bus
    )
    
    if pdf:
        response = pdf
        filename = f"ticket_{booking.booking_reference}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    messages.error(request, 'Could not generate ticket PDF.')
    return redirect('booking_confirmation', booking_id=booking.id)