from django import forms
from . models import ParkingSlot

class ParkingSlotCreationForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = "__all__"

        labels = {
            'name': 'Service Name (e.g., Car Wash, Engine Repair, Full Service)',
            'is_booked': 'Is this service currently unavailable?',
            'parkingImage': 'Upload Service/Mechanic Image'
        }