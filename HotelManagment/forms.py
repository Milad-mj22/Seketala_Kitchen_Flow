from django import forms
from .models import HotelRoom, Guest

class HotelRoomForm(forms.ModelForm):
    class Meta:
        model = HotelRoom
        fields = ["room_number", "room_capacity", "room_type", "description"]

class GuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        fields = ["room", "first_name", "last_name", "national_code", "phone_number", "date_in", "date_out", "persons_in_room"]
