from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from DataAnalysis import views



urlpatterns = [

    path('upload-db/', views.upload_db, name='upload_db'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("api/receive-invoice/", views.ReceiveInvoice.as_view()),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)