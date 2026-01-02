from django.db import models

# Create your models here.



class HotelRoom(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_capacity = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=50, blank=True, null=True)  # optional
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_capacity} persons)"


class Guest(models.Model):
    room = models.ForeignKey(HotelRoom, on_delete=models.CASCADE, related_name="guests")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    national_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    date_in = models.DateField()
    date_out = models.DateField()
    persons_in_room = models.PositiveIntegerField(default=1)

    show_in_list = models.BooleanField(default=True)  # True for only show for projects

    def __str__(self):
        return f"{self.first_name} {self.last_name} in Room {self.room.room_number}"