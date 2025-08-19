from django.db import models

# Create your models here.
class Camera(models.Model):
    name = models.CharField(max_length=255)  # Name of the camera
    ip_address = models.GenericIPAddressField()  # IP address of the camera
    port = models.PositiveIntegerField()  # Port for the camera connection
    username = models.CharField(max_length=255)  # Username for camera access
    password = models.CharField(max_length=255)  # Password for camera access
    is_active = models.BooleanField(default=True)  # Whether the camera is active or not
    last_connected = models.DateTimeField(auto_now=True)  # Timestamp of last connection
    # Optionally, you can add other fields like camera type, description, or location
    location = models.CharField(max_length=255, blank=True, null=True)  # Location of the camera
    description = models.TextField(blank=True, null=True)  # Camera description

    def __str__(self):
        return self.name

    def get_live_feed_url(self):
        # Assuming the live feed is accessed via a specific URL pattern or IP stream.
        # Modify this as per your camera's configuration.
        return f"http://{self.ip_address}:{self.port}/live"
    


from django.db import models
from django.contrib.auth.models import User

class DetectedPersons(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)  # Name of the person
    detected_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the person was detected
    camera = models.ForeignKey('Camera', on_delete=models.CASCADE, related_name='detected_persons')  # The camera that detected the person
    image = models.ImageField(upload_to='detected_persons/', blank=True, null=True)  # Optional image of the detected person
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_persons')  # User assigned to this person
    embed_code = models.CharField(max_length=300, blank=True, null=True) 



    def __str__(self):
        return self.name if self.name else f"Person detected at {self.detected_at}"

    def get_assigned_user(self):
        return self.assigned_user.username if self.assigned_user else "Not assigned"
