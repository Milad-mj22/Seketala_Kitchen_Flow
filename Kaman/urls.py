
from django.urls import path

from .views import register_phone , home
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('', home, name='index'),
    path('register-phone/', register_phone, name='register_phone'),
    # path('demo/', views.demo_view, name='demo'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
