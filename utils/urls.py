from django.urls import path
from .views import import_buyers_csv, import_composition_materials_csv, import_raw_materials_csv, manage_inventory, ticket_create, ticket_detail, ticket_list

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('import-buyers-csv/', import_buyers_csv, name='import_buyers_csv'),
    path('import-materilas-csv/', import_raw_materials_csv, name='import_raw_materials_csv'),
    path('import-material_composotion-csv/', import_composition_materials_csv, name='import_composition_materials_csv'),
    path("manage/", manage_inventory, name="manage_inventory"),


    path('tickets/', ticket_list, name='ticket_list'),
    path('tickets/create/', ticket_create, name='ticket_create'),
    path('tickets/<int:ticket_id>/', ticket_detail, name='ticket_detail'),











] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)















