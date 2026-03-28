# from django.db import models
# from apps.accounts.models import User
# from apps.bus_owners.models import Route, Seat

# class Booking(models.Model):
#     BOOKING_STATUS = (
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('cancelled', 'Cancelled'),
#         ('completed', 'Completed'),
#     )
    
#     user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'}, related_name='customer_bookings')
#     route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_bookings')
#     booking_date = models.DateTimeField(auto_now_add=True)
#     journey_date = models.DateField()
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
#     payment_id = models.CharField(max_length=100, blank=True, null=True)
#     payment_method = models.CharField(max_length=50, blank=True, null=True)
#     booking_reference = models.CharField(max_length=20, unique=True)
    
#     def __str__(self):
#         return f"{self.booking_reference} - {self.user.username}"

# class BookedSeat(models.Model):
#     GENDER_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#     )
    
#     booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
#     seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='seat_bookings')
#     passenger_name = models.CharField(max_length=100)
#     passenger_age = models.IntegerField()
#     passenger_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
#     passenger_adhar = models.CharField(max_length=12, blank=True, null=True)
    
#     class Meta:
#         unique_together = ['booking', 'seat']
    
#     def __str__(self):
#         return f"{self.seat.seat_number} - {self.passenger_name}"

# class Payment(models.Model):
#     PAYMENT_METHODS = (
#         ('googlepay', 'Google Pay'),
#         ('phonepe', 'PhonePe'),
#         ('paytm', 'Paytm'),
#         ('bhim', 'BHIM UPI'),
#         ('credit_card', 'Credit Card'),
#         ('debit_card', 'Debit Card'),
#         ('netbanking', 'Net Banking'),
#     )
    
#     PAYMENT_STATUS = (
#         ('pending', 'Pending'),
#         ('success', 'Success'),
#         ('failed', 'Failed'),
#     )
    
#     booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
#     transaction_id = models.CharField(max_length=100, unique=True)
#     payment_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='success')
    
#     def __str__(self):
#         return f"{self.transaction_id} - ₹{self.amount}"


# # from django.db import models
# # from apps.accounts.models import User
# # from apps.bus_owners.models import Route, Seat


# # class Booking(models.Model):
# #     BOOKING_STATUS = (
# #         ('pending', 'Pending'),
# #         ('confirmed', 'Confirmed'),
# #         ('cancelled', 'Cancelled'),
# #         ('completed', 'Completed'),
# #     )

# #     user = models.ForeignKey(
# #         User, on_delete=models.CASCADE,
# #         limit_choices_to={'user_type': 'customer'},
# #         related_name='customer_bookings'
# #     )
# #     route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_bookings')
# #     booking_date = models.DateTimeField(auto_now_add=True)
# #     journey_date = models.DateField()
# #     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
# #     status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
# #     payment_id = models.CharField(max_length=100, blank=True, null=True)
# #     payment_method = models.CharField(max_length=50, blank=True, null=True)
# #     booking_reference = models.CharField(max_length=20, unique=True)

# #     # FIX: Added cancellation_reason field that was referenced in views but missing
# #     cancellation_reason = models.TextField(blank=True, null=True)

# #     def __str__(self):
# #         return f"{self.booking_reference} - {self.user.username}"


# # class BookedSeat(models.Model):
# #     GENDER_CHOICES = (
# #         ('M', 'Male'),
# #         ('F', 'Female'),
# #         ('O', 'Other'),
# #     )

# #     booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
# #     seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='seat_bookings')
# #     passenger_name = models.CharField(max_length=100)
# #     passenger_age = models.IntegerField()
# #     passenger_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

# #     # FIX: Store only last 4 digits of Aadhaar — never store full number
# #     # On save, automatically mask: "XXXX-XXXX-1234"
# #     passenger_adhar_last4 = models.CharField(max_length=4, blank=True, null=True,
# #                                               help_text="Last 4 digits of Aadhaar only")

# #     class Meta:
# #         unique_together = ['booking', 'seat']

# #     def set_adhar(self, full_adhar):
# #         """Accept full 12-digit number, store only last 4."""
# #         if full_adhar and len(str(full_adhar)) >= 4:
# #             self.passenger_adhar_last4 = str(full_adhar)[-4:]

# #     def get_masked_adhar(self):
# #         if self.passenger_adhar_last4:
# #             return f"XXXX-XXXX-{self.passenger_adhar_last4}"
# #         return "Not provided"

# #     def __str__(self):
# #         return f"{self.seat.seat_number} - {self.passenger_name}"


# # class Payment(models.Model):
# #     PAYMENT_METHODS = (
# #         ('razorpay', 'Razorpay'),
# #         ('googlepay', 'Google Pay'),
# #         ('phonepe', 'PhonePe'),
# #         ('paytm', 'Paytm'),
# #         ('bhim', 'BHIM UPI'),
# #         ('credit_card', 'Credit Card'),
# #         ('debit_card', 'Debit Card'),
# #         ('netbanking', 'Net Banking'),
# #     )

# #     PAYMENT_STATUS = (
# #         ('pending', 'Pending'),
# #         ('success', 'Success'),
# #         ('failed', 'Failed'),
# #     )

# #     booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
# #     amount = models.DecimalField(max_digits=10, decimal_places=2)
# #     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
# #     transaction_id = models.CharField(max_length=100, unique=True)
# #     # FIX: Added razorpay_order_id for real Razorpay integration
# #     razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
# #     payment_date = models.DateTimeField(auto_now_add=True)
# #     status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

# #     def __str__(self):
# #         return f"{self.transaction_id} - ₹{self.amount}"


from django.db import models
from apps.accounts.models import User
from apps.bus_owners.models import Route, Seat

class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'customer'}, related_name='customer_bookings')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    journey_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    booking_reference = models.CharField(max_length=20, unique=True)
    
    # Add these missing fields for cancellation
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_status = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.user.username}"
    
    def can_cancel(self):
        """Check if booking can be cancelled"""
        from django.utils import timezone
        if self.status == 'cancelled':
            return False
        # Can cancel up to 4 hours before departure
        time_diff = self.journey_date - timezone.now().date()
        return time_diff.days >= 0

class BookedSeat(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='booked_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='seat_bookings')
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.IntegerField()
    passenger_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    passenger_adhar = models.CharField(max_length=12, blank=True, null=True)
    
    class Meta:
        unique_together = ['booking', 'seat']
    
    def __str__(self):
        return f"{self.seat.seat_number} - {self.passenger_name}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('googlepay', 'Google Pay'),
        ('phonepe', 'PhonePe'),
        ('paytm', 'Paytm'),
        ('bhim', 'BHIM UPI'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('netbanking', 'Net Banking'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='success')
    refund_date = models.DateTimeField(blank=True, null=True)
    refund_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.transaction_id} - ₹{self.amount}"