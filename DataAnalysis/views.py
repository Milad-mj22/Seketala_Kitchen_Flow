from django.shortcuts import render

# Create your views here.
# views.py
import os
import sqlite3
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import DBUploadForm
from .models import InvoiceItem, Sale
from persiantools.jdatetime import JalaliDate


def upload_db(request):
    if request.method == "POST":
        form = DBUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            temp_path = os.path.join(settings.MEDIA_ROOT, uploaded_file.name)
            with open(temp_path, "wb+") as dest:
                for chunk in uploaded_file.chunks():
                    dest.write(chunk)

            # Connect to uploaded DB
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            try:
                cursor.execute("SELECT factnum, dat, total, kname, tel, adress FROM facts")  # adjust table name
                rows = cursor.fetchall()

                # Import data
                for row in rows:


                    jalali_str = row[1]  # example: "03/10/27"

                    # Clean and parse Jalali date (assuming format: YY/MM/DD or YYYY/MM/DD)
                    try:
                        parts = jalali_str.replace("“", "").replace("”", "").split("/")
                        if len(parts[0]) == 2:
                            # If year is short like 03 → convert to 1403
                            year = int(parts[0]) + 1400
                        else:
                            year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])

                        gregorian_date = JalaliDate(year, month, day).to_gregorian()
                    except Exception as e:
                        #print(f"⚠️ Error converting date {jalali_str}: {e}")
                        continue  # skip bad records








                    Sale.objects.get_or_create(
                        factnum=row[0],
                        defaults={
                            'dat': gregorian_date,
                            'total': row[2],
                            'kname': row[3],
                            'tel': row[4],
                            'address': row[5],
                        }
                    )
                conn.close()
                os.remove(temp_path)
                return render(request, "UploadDB/upload_success.html", {"count": len(rows)})

            except Exception as e:
                conn.close()
                return render(request, "UploadDB/upload_error.html", {"error": str(e)})

    else:
        form = DBUploadForm()

    return render(request, "UploadDB/upload_db.html", {"form": form})


from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate

from django.shortcuts import render
from django.db.models import Sum
from django.db.models.functions import TruncDate

from .models import Invoice, InvoiceItem


from django.db.models import Sum

def dashboard(request):
    top_customers = (
        Invoice.objects.values('phone')
        .annotate(total_spent=Sum('total_price'))
        .order_by('-total_spent')[:10]
    )

    daily_qs = (
        Invoice.objects
        .values('created_at__date')
        .annotate(total_day=Sum('total_price'))
        .order_by('created_at__date')
    )

    summary = Invoice.objects.aggregate(
        total_revenue=Sum('total_price')
    )

    daily_item_volume = (
        InvoiceItem.objects
        .annotate(day=TruncDate('invoice__created_at'))
        .values('day')
        .annotate(total_qty=Sum('quantity'))
        .order_by('day')
    )

    context = {
        'top_customers': top_customers,
        'daily_sales': daily_qs,
        'total_revenue': summary['total_revenue'] or 0,  # تومان
        'days_count': daily_qs.count(),
        'customers_count': Invoice.objects.values('phone').distinct().count(),
        'daily_item_volume': daily_item_volume,
    }

    return render(request, 'factors_data_dashboard.html', context)








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Invoice
from .utils import extract_payment_methods, jalali_date_time_to_gregorian




class ReceiveInvoice(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        data = request.data
        if request.headers.get("X-API-KEY") != "SECRET123":
            return Response({"error": "unauthorized"}, status=403)
    
        
        
        date_time = jalali_date_time_to_gregorian(data['date'],data['time'])

        invoice, created = Invoice.objects.get_or_create(
            invoice_number=data["invoice_number"],
            defaults={
                "name": data["name"],
                "nahveh": data["nahveh"],
                "phone": data["phone"],
                "created_at": date_time,
                "total_price": data["total_price"],
            }
        )

        if not created:
            return Response({"status": "already_exists"})

        for item in data["items"]:
            InvoiceItem.objects.create(
                invoice=invoice,
                food_name=item["food"],
                price=item["price"],
                quantity=item["quantity"],
                total=item["price"] * item["quantity"]
            )

        return Response({"status": "ok"}, status=status.HTTP_201_CREATED)
    

from django.db.models import Max
from collections import defaultdict
from datetime import datetime
import re

def calc_nahve_pardakh(request):
    date_str = request.GET.get('date')

    # 🔹 اگر تاریخ نفرستاده بود → آخرین تاریخ دیتابیس
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y/%m/%d').date()
    else:
        last_date = Invoice.objects.aggregate(
            max_date=Max('created_at')
        )['max_date']

        if not last_date:
            return render(request, 'nahve.html', {})

        selected_date = last_date.date()

    invoices = Invoice.objects.filter(
        created_at__date=selected_date
    )

    totals = defaultdict(int)

    for invoice in invoices:
        if 'اسنپ' not in invoice.name:
            methods = extract_payment_methods(invoice.nahveh)
            for method in methods:
                totals[method] += invoice.total_price
        else:
   
            totals['اسنپ']  += invoice.total_price
  

    context = {
        'selected_date': selected_date,
        'labels': list(totals.keys()),
        'values': list(totals.values()),
        'table_data': totals.items()
    }

    return render(request, 'utils/nahve.html', context)
