from django.db import models
from cameras.VidGear import UrlGenerator

class AIFeatureName(models.Model):
    FEATURE_TYPES = [
        ('object_detection', 'Object Detection'),
        ('face_recognition', 'Face Recognition'),
        ('mask_detection', 'Mask Detection'),
        ('face_detection', 'Face Detection'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100, choices=FEATURE_TYPES, unique=True)
    description = models.TextField(blank=True, null=True)  # توضیح قابلیت

    def __str__(self):
        return self.get_name_display()
    


class Camera(models.Model):
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    last_connected = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Many-to-Many relationship to AI features
    ai_features = models.ManyToManyField(AIFeatureName, blank=True, related_name='cameras')

    def __str__(self):
        return self.name

    def get_live_feed_url(self):
        return UrlGenerator(self.ip_address,self.port,self.username,self.password)


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
