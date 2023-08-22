from django.contrib import admin
from .models import PPPCalculation

# Register your models here.


class PPPCalculationAdmin(admin.ModelAdmin):
    search_fields = ["country_name", "currency_name", "currency_code"]


admin.site.register(PPPCalculation, PPPCalculationAdmin)
