from django.db import models

# Create your models here.


class PhoneLead(models.Model):
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)