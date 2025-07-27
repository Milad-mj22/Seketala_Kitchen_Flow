from django.urls import path
from .views import import_buyers_csv, import_raw_materials_csv

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('import-buyers-csv/', import_buyers_csv, name='import_buyers_csv'),
    path('import-materilas-csv/', import_raw_materials_csv, name='import_buyers_csv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
