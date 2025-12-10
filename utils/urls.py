from django.urls import path
from .views import import_buyers_csv, import_composition_materials_csv, import_raw_materials_csv, manage_inventory,import_tasks_csv, ticket_create, ticket_created, ticket_detail, ticket_list, project_ticket_create

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

    path('tickets/', ticket_list, name='ticket_list'),
    path('tickets/create/', ticket_create, name='ticket_create'),
    path('tickets/create/<int:project_id>', project_ticket_create, name='ticket_project_create'),
    path('tickets/<int:ticket_id>/', ticket_detail, name='ticket_detail'),
    path('ticket_created/<int:ticket_number>/', ticket_created, name='ticket_created'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
