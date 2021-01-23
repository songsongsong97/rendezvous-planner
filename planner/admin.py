from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Todo)
admin.site.register(Plan)
admin.site.register(DailyExpense)
admin.site.register(Member)
