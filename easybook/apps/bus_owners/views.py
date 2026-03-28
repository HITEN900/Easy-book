from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Bus, Route, BusStop, Seat, OwnerBankDetails
from apps.bookings.models import Booking
from django.utils import timezone
import json
import random
import string

# Helper function to generate booking reference
def generate_booking_reference():
    return 'BK' + ''.join(random.choices(string.digits, k=8))

# Helper function to create seats for a bus based on layout
def create_seats_for_bus(bus, layout, total_seats):
    """Helper function to create seats based on layout"""
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
    
    elif layout == '2x1':
        rows = (total_seats + 2) // 3
        for row in range(1, rows + 1):
            for col in range(1, 4):
                if seat_number <= total_seats:
                    if col == 1 or col == 3:
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
    
    elif layout == 'sleeper_2x1':
        rows = (total_seats + 2) // 3
        for row in range(1, rows + 1):
            for col in range(1, 4):
                if seat_number <= total_seats:
                    if col == 1:
                        seat_type = 'sleeper_lower'
                    elif col == 2:
                        seat_type = 'sleeper_upper'
                    else:
                        seat_type = 'sleeper_lower'
                    
                    Seat.objects.create(
                        bus=bus,
                        seat_number=f'{row}{chr(64+col)}',
                        seat_type=seat_type,
                        seat_row=row,
                        seat_column=col,
                        is_active=True
                    )
                    seat_number += 1

# Bus Owner Registration
def bus_owner_registration(request):
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        address = request.POST.get('address')
        license_number = request.POST.get('license_number')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        
        messages.success(request, 'Please create an account to continue with bus owner registration.')
        return redirect('signup')
    
    return render(request, 'bus_owner/register.html')

# Bus Owner Dashboard
@login_required
def bus_owner_dashboard(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    # Get all buses for this owner
    buses = Bus.objects.filter(owner=request.user)
    
    # Calculate statistics
    total_buses = buses.count()
    active_buses = buses.filter(is_active=True).count()
    
    # Get all routes from these buses
    all_routes = Route.objects.filter(bus__in=buses)
    total_routes = all_routes.count()
    active_routes = all_routes.filter(available_seats__gt=0).count()
    
    # Get all bookings for these routes
    all_bookings = Booking.objects.filter(route__in=all_routes)
    total_bookings = all_bookings.count()
    
    # Calculate total earnings from confirmed bookings
    total_earnings = all_bookings.filter(status='confirmed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Get recent buses (last 5)
    recent_buses = buses.order_by('-created_at')[:5]
    
    # Get recent bookings (last 5)
    recent_bookings = all_bookings.order_by('-booking_date')[:5]
    
    context = {
        'buses': buses,
        'recent_buses': recent_buses,
        'recent_bookings': recent_bookings,
        'total_buses': total_buses,
        'active_buses': active_buses,
        'total_routes': total_routes,
        'active_routes': active_routes,
        'total_bookings': total_bookings,
        'total_earnings': total_earnings,
    }
    return render(request, 'bus_owner/dashboard.html', context)

# Add Bus
@login_required
def add_bus(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    if request.method == 'POST':
        bus_name = request.POST.get('bus_name')
        bus_type = request.POST.get('bus_type')
        bus_number = request.POST.get('bus_number')
        total_seats = request.POST.get('total_seats')
        seat_layout = request.POST.get('seat_layout')
        amenities = request.POST.get('amenities', '')
        
        # Validate inputs
        if not all([bus_name, bus_type, bus_number, total_seats, seat_layout]):
            messages.error(request, 'Please fill all required fields.')
            return render(request, 'bus_owner/add_bus.html')
        
        try:
            # Check if bus number already exists
            if Bus.objects.filter(bus_number=bus_number).exists():
                messages.error(request, 'Bus number already exists. Please use a different number.')
                return render(request, 'bus_owner/add_bus.html')
            
            # Handle image upload
            bus_image = request.FILES.get('bus_image')
            
            # Create bus
            bus = Bus.objects.create(
                owner=request.user,
                bus_name=bus_name,
                bus_type=bus_type,
                bus_number=bus_number,
                total_seats=int(total_seats),
                seat_layout=seat_layout,
                amenities=amenities,
                bus_image=bus_image,
                is_active=True
            )
            
            # Create seats based on layout
            create_seats_for_bus(bus, seat_layout, int(total_seats))
            
            messages.success(request, f'Bus "{bus_name}" added successfully! Now add routes for this bus.')
            return redirect('manage_routes', bus_id=bus.id)
            
        except Exception as e:
            messages.error(request, f'Error adding bus: {str(e)}')
            return render(request, 'bus_owner/add_bus.html')
    
    return render(request, 'bus_owner/add_bus.html')

# Manage Buses
@login_required
def manage_buses(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    buses = Bus.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'bus_owner/manage_buses.html', {'buses': buses})

# Edit Bus
@login_required
def edit_bus(request, bus_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    bus = get_object_or_404(Bus, id=bus_id, owner=request.user)
    
    if request.method == 'POST':
        bus.bus_name = request.POST.get('bus_name')
        bus.bus_type = request.POST.get('bus_type')
        bus.bus_number = request.POST.get('bus_number')
        bus.amenities = request.POST.get('amenities')
        bus.is_active = request.POST.get('is_active') == 'on'
        bus.save()
        
        messages.success(request, 'Bus updated successfully!')
        return redirect('manage_buses')
    
    return render(request, 'bus_owner/edit_bus.html', {'bus': bus})

# Delete Bus
@login_required
def delete_bus(request, bus_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    bus = get_object_or_404(Bus, id=bus_id, owner=request.user)
    
    if request.method == 'POST':
        bus_name = bus.bus_name
        bus.delete()
        messages.success(request, f'Bus "{bus_name}" deleted successfully!')
    
    return redirect('manage_buses')

# Add Route
@login_required
def add_route(request, bus_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    bus = get_object_or_404(Bus, id=bus_id, owner=request.user)
    
    if request.method == 'POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        fare = request.POST.get('fare')
        operating_days = request.POST.get('operating_days', 'All Days')
        
        # Calculate duration
        dep_time = timezone.datetime.fromisoformat(departure_time)
        arr_time = timezone.datetime.fromisoformat(arrival_time)
        duration = arr_time - dep_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds // 60) % 60
        duration_str = f"{hours} hours {minutes} minutes"
        
        try:
            route = Route.objects.create(
                bus=bus,
                source=source,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                duration=duration_str,
                fare=float(fare),
                operating_days=operating_days,
                available_seats=bus.total_seats
            )
            
            messages.success(request, f'Route from {source} to {destination} added successfully!')
            return redirect('manage_routes', bus_id=bus.id)
            
        except Exception as e:
            messages.error(request, f'Error adding route: {str(e)}')
            return render(request, 'bus_owner/add_route.html', {'bus': bus})
    
    return render(request, 'bus_owner/add_route.html', {'bus': bus})

# Manage Routes
@login_required
def manage_routes(request, bus_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    bus = get_object_or_404(Bus, id=bus_id, owner=request.user)
    routes = Route.objects.filter(bus=bus).order_by('departure_time')
    
    return render(request, 'bus_owner/manage_routes.html', {'bus': bus, 'routes': routes})

# Edit Route
@login_required
def edit_route(request, route_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    route = get_object_or_404(Route, id=route_id, bus__owner=request.user)
    
    if request.method == 'POST':
        route.source = request.POST.get('source')
        route.destination = request.POST.get('destination')
        route.departure_time = request.POST.get('departure_time')
        route.arrival_time = request.POST.get('arrival_time')
        route.fare = request.POST.get('fare')
        route.operating_days = request.POST.get('operating_days')
        route.save()
        
        messages.success(request, 'Route updated successfully!')
        return redirect('manage_routes', bus_id=route.bus.id)
    
    return render(request, 'bus_owner/edit_route.html', {'route': route})

# Delete Route
@login_required
def delete_route(request, route_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    route = get_object_or_404(Route, id=route_id, bus__owner=request.user)
    bus_id = route.bus.id
    
    if request.method == 'POST':
        route.delete()
        messages.success(request, 'Route deleted successfully!')
    
    return redirect('manage_routes', bus_id=bus_id)

# Bus Seat Layout
@login_required
def bus_seat_layout(request, bus_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    bus = get_object_or_404(Bus, id=bus_id, owner=request.user)
    seats = Seat.objects.filter(bus=bus).order_by('seat_row', 'seat_column')
    
    # Organize seats by row for display
    seat_rows = {}
    for seat in seats:
        if seat.seat_row not in seat_rows:
            seat_rows[seat.seat_row] = []
        seat_rows[seat.seat_row].append(seat)
    
    return render(request, 'bus_owner/seat_layout.html', {
        'bus': bus,
        'seat_rows': dict(sorted(seat_rows.items()))
    })

# Update Seat Status
@login_required
def update_seat_status(request, seat_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    seat = get_object_or_404(Seat, id=seat_id, bus__owner=request.user)
    
    if request.method == 'POST':
        # Update seat status logic here
        messages.success(request, f'Seat {seat.seat_number} status updated!')
    
    return redirect('bus_seat_layout', bus_id=seat.bus.id)

# ============= UPDATED BUS BOOKINGS VIEW WITH SEAT NUMBERS AND STATISTICS =============
@login_required
def bus_bookings(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    buses = Bus.objects.filter(owner=request.user)
    all_routes = Route.objects.filter(bus__in=buses)
    
    # Get all bookings
    bookings = Booking.objects.filter(route__in=all_routes).order_by('-booking_date')
    
    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        bookings = bookings.filter(status=status)
    
    # Filter by bus if provided
    bus_id = request.GET.get('bus')
    if bus_id:
        bookings = bookings.filter(route__bus_id=bus_id)
    
    # Calculate statistics
    total_bookings = Booking.objects.filter(route__in=all_routes).count()
    confirmed_bookings = Booking.objects.filter(route__in=all_routes, status='confirmed').count()
    pending_bookings = Booking.objects.filter(route__in=all_routes, status='pending').count()
    cancelled_bookings = Booking.objects.filter(route__in=all_routes, status='cancelled').count()
    
    context = {
        'bookings': bookings,
        'buses': buses,
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
    }
    return render(request, 'bus_owner/bookings.html', context)

# View Booking Details
@login_required
def booking_details(request, booking_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id, route__bus__owner=request.user)
    booked_seats = booking.booked_seats.all()
    
    return render(request, 'bus_owner/booking_details.html', {
        'booking': booking,
        'booked_seats': booked_seats
    })

# Update Booking Status
@login_required
def update_booking_status(request, booking_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    booking = get_object_or_404(Booking, id=booking_id, route__bus__owner=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        booking.status = new_status
        booking.save()
        
        messages.success(request, f'Booking status updated to {new_status}!')
    
    return redirect('booking_details', booking_id=booking.id)

# Add Bus Stop
@login_required
def add_bus_stop(request, route_id):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    route = get_object_or_404(Route, id=route_id, bus__owner=request.user)
    
    if request.method == 'POST':
        stop_name = request.POST.get('stop_name')
        stop_order = request.POST.get('stop_order')
        arrival_time = request.POST.get('arrival_time')
        departure_time = request.POST.get('departure_time')
        stop_duration = request.POST.get('stop_duration', 5)
        
        BusStop.objects.create(
            route=route,
            stop_name=stop_name,
            stop_order=stop_order,
            arrival_time=arrival_time,
            departure_time=departure_time,
            stop_duration=stop_duration
        )
        
        messages.success(request, f'Stop "{stop_name}" added successfully!')
        return redirect('manage_routes', bus_id=route.bus.id)
    
    return render(request, 'bus_owner/add_bus_stop.html', {'route': route})

# Earnings Report
@login_required
def earnings_report(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    buses = Bus.objects.filter(owner=request.user)
    all_routes = Route.objects.filter(bus__in=buses)
    bookings = Booking.objects.filter(route__in=all_routes, status='confirmed')
    
    # Calculate total earnings
    total_earnings = bookings.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Get monthly earnings
    monthly_earnings = bookings.annotate(
        month=TruncMonth('booking_date')
    ).values('month').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        'total_earnings': total_earnings,
        'total_bookings': bookings.count(),
        'monthly_earnings': monthly_earnings,
        'buses': buses,
    }
    return render(request, 'bus_owner/earnings.html', context)

# Owner Booking Statistics
@login_required
def owner_booking_stats(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    # Get all buses for this owner
    buses = Bus.objects.filter(owner=request.user)
    
    # Get all routes from these buses
    all_routes = Route.objects.filter(bus__in=buses)
    
    # Get all bookings for these routes
    bookings = Booking.objects.filter(route__in=all_routes).order_by('-booking_date')
    
    # Calculate statistics
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    pending_bookings = bookings.filter(status='pending').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    
    # Calculate total earnings from confirmed bookings
    total_earnings = bookings.filter(status='confirmed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Get monthly earnings for chart
    monthly_earnings = bookings.filter(status='confirmed').annotate(
        month=TruncMonth('booking_date')
    ).values('month').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('month')
    
    # Get recent bookings
    recent_bookings = bookings[:10]
    
    context = {
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_earnings': total_earnings,
        'monthly_earnings': monthly_earnings,
        'recent_bookings': recent_bookings,
        'buses': buses,
    }
    return render(request, 'bus_owner/booking_stats.html', context)

# Add Bank Details
@login_required
def add_bank_details(request):
    if request.user.user_type != 'bus_owner':
        messages.error(request, 'Access denied. Bus owner only.')
        return redirect('home')
    
    try:
        bank_details = OwnerBankDetails.objects.get(owner=request.user)
    except OwnerBankDetails.DoesNotExist:
        bank_details = None
    
    if request.method == 'POST':
        account_holder_name = request.POST.get('account_holder_name')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        upi_id = request.POST.get('upi_id')
        phonepe_number = request.POST.get('phonepe_number')
        googlepay_number = request.POST.get('googlepay_number')
        paytm_number = request.POST.get('paytm_number')
        qr_code = request.FILES.get('qr_code')
        
        if bank_details:
            # Update existing
            bank_details.account_holder_name = account_holder_name
            bank_details.bank_name = bank_name
            bank_details.account_number = account_number
            bank_details.ifsc_code = ifsc_code
            bank_details.upi_id = upi_id
            bank_details.phonepe_number = phonepe_number
            bank_details.googlepay_number = googlepay_number
            bank_details.paytm_number = paytm_number
            if qr_code:
                bank_details.qr_code = qr_code
            bank_details.save()
            messages.success(request, 'Bank details updated successfully!')
        else:
            # Create new
            OwnerBankDetails.objects.create(
                owner=request.user,
                account_holder_name=account_holder_name,
                bank_name=bank_name,
                account_number=account_number,
                ifsc_code=ifsc_code,
                upi_id=upi_id,
                phonepe_number=phonepe_number,
                googlepay_number=googlepay_number,
                paytm_number=paytm_number,
                qr_code=qr_code
            )
            messages.success(request, 'Bank details added successfully!')
        
        return redirect('owner_booking_stats')
    
    context = {
        'bank_details': bank_details
    }
    return render(request, 'bus_owner/bank_details.html', context)