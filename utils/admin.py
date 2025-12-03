from django.contrib import admin

# Register your models here.
from utils.models import Ticket, TicketCategory

# Register your models here.
admin.site.register(TicketCategory)
admin.site.register(Ticket)