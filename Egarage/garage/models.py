from django.db import models
from django.conf import settings

# Create your models here.

class ParkingSlot(models.Model):
    name = models.CharField(max_length=100)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parkingImage = models.ImageField(upload_to='parking_images/')
    booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    
    def __str__(self):
        return self.name
    