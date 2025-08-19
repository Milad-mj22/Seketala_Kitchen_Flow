from django import forms

from cameras.models import Camera



class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['name', 'ip_address', 'port', 'username', 'password', 'location', 'description']
        widgets = {
            'password': forms.PasswordInput(),
        }