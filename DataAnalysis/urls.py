from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from DataAnalysis import views



urlpatterns = [

    path('upload-db/', views.upload_db, name='upload_db'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('nahve/', views.calc_nahve_pardakh, name='calc_nahve_pardakht'),
    path("api/receive-invoice/", views.ReceiveInvoice.as_view()),
    path("report/", views.invoice_report, name="invoice_report"),
    path("report/download/", views.download_invoice_excel, name="download_invoice_excel"),
    path("report/download-summary/", views.sepidar_download_excel, name="download_invoice_summary_excel"),
    path(
        "api/invoices/<str:invoice_number>/",
        views.invoice_detail_api,
        name="invoice_detail_api"
    ),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)