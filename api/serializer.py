# api/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User

class ExternalRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField()
    name = serializers.CharField()
    company = serializers.CharField(required=False)

    def validate_phone(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("User already exists")
        return value
