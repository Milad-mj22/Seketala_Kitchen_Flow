from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import PhoneLead
from django.utils import timezone

def register_phone(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        if phone.startswith('09') and len(phone) == 11:
            PhoneLead.objects.create(
                phone=phone,
                created_at=timezone.now(),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            request.session['phone'] = phone
            return redirect('/demo/')
    return redirect('/')



def home(request):

    return render(request, 'landing.html')