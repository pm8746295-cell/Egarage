from django import forms
from . models import ParkingSlot

class ParkingSlotCreationForm(forms.ModelForm):
    class Meta:
        model = ParkingSlot
        fields = "__all__"