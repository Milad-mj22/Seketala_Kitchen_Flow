from django.urls import path
from .views import import_buyers_csv, import_composition_materials_csv, import_raw_materials_csv, manage_inventory,import_tasks_csv

from django.conf import settings
from django.conf.urls.static import static
from timeTracker.views import team_list

urlpatterns = [
    path('import-buyers-csv/', import_buyers_csv, name='import_buyers_csv'),
    path('import-materilas-csv/', import_raw_materials_csv, name='import_raw_materials_csv'),
    path('import-material_composotion-csv/', import_composition_materials_csv, name='import_composition_materials_csv'),
    path("manage/", manage_inventory, name="manage_inventory"),
    path('teams/', team_list, name='team_list'),
    path('import_tasks_csv/', import_tasks_csv, name='import_tasks_csv'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
