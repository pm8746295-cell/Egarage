from django import forms
from .models import ParkingSlot

class ParkingSlotCreationForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        # Yahan specifically 'amount' add kiya hai aur faltu fields hataye hain
        fields = ['name', 'amount', 'parkingImage', 'is_booked']

        labels = {
            'name': 'Service Name (e.g., Car Wash, Engine Repair, Full Service)',
            'amount': 'Service Price / Amount (₹)',
            'is_booked': 'Is this service currently unavailable?',
            'parkingImage': 'Upload Service/Mechanic Image'
        }