from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Sprint,Story,Task,Team


admin.site.register(Sprint)
admin.site.register(Story)
admin.site.register(Task)
admin.site.register(Team)