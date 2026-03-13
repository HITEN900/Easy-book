from django.db import models
from apps.accounts.models import User

class Bus(models.Model):
    BUS_TYPES = (
        ('ac', 'AC'),
        ('non_ac', 'Non AC'),
        ('sleeper', 'Sleeper'),
        ('seater', 'Seater'),
        ('ac_sleeper', 'AC Sleeper'),
        ('luxury', 'Luxury'),
    )
    
    BUS_LAYOUTS = (
        ('2x2', '2 x 2 (4 seats per row)'),
        ('2x1', '2 x 1 (3 seats per row)'),
        ('1x2', '1 x 2 (3 seats per row)'),
        ('sleeper_2x1', 'Sleeper 2 x 1'),
        ('sleeper_1x1', 'Sleeper 1 x 1'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'bus_owner'}, related_name='buses')
    bus_name = models.CharField(max_length=100)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    bus_number = models.CharField(max_length=20, unique=True)
    total_seats = models.IntegerField()
    seat_layout = models.CharField(max_length=20, choices=BUS_LAYOUTS, default='2x2')
    amenities = models.TextField(help_text="AC, WiFi, Charging point, etc.", blank=True)
    bus_image = models.ImageField(upload_to='bus_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bus_name} - {self.bus_number}"

class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.CharField(max_length=50, help_text="e.g., 5 hours 30 mins", blank=True)
    fare = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.IntegerField()
    operating_days = models.CharField(max_length=100, help_text="Mon,Tue,Wed,Thu,Fri,Sat,Sun", default="All Days")
    
    def __str__(self):
        return f"{self.source} to {self.destination} - ₹{self.fare}"

class BusStop(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops')
    stop_name = models.CharField(max_length=100)
    stop_order = models.IntegerField(help_text="Order of stop in the journey")
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_duration = models.IntegerField(help_text="Duration in minutes", default=5)
    
    class Meta:
        ordering = ['stop_order']
    
    def __str__(self):
        return f"{self.stop_name} - {self.arrival_time}"

class Seat(models.Model):
    SEAT_TYPES = (
        ('window', 'Window'),
        ('aisle', 'Aisle'),
        ('middle', 'Middle'),
        ('sleeper_lower', 'Sleeper Lower'),
        ('sleeper_upper', 'Sleeper Upper'),
    )
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPES, default='window')
    seat_row = models.IntegerField()
    seat_column = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['bus', 'seat_number']
        ordering = ['seat_row', 'seat_column']
    
    def __str__(self):
        return f"{self.bus.bus_number} - Seat {self.seat_number}"

class OwnerBankDetails(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'bus_owner'}, related_name='bank_details')
    account_holder_name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    upi_id = models.CharField(max_length=50, help_text="Enter your UPI ID (e.g., name@okhdfcbank)")
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    phonepe_number = models.CharField(max_length=15, blank=True, null=True)
    googlepay_number = models.CharField(max_length=15, blank=True, null=True)
    paytm_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.owner.username}'s Bank Details"