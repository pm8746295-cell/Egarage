from django.db import models
from django.conf import settings

class ParkingSlot(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    # Nayi line: Owner ke liye (related_name zaroori hai taaki error na aaye)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_services', null=True)
    
    name = models.CharField(max_length=100)
    # Ye amount wali line aapki miss ho gayi thi
    amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True) 
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parkingImage = models.ImageField(upload_to='parking_images/')
    
    # Book karne wale user ke liye
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_services'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name