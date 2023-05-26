from django.contrib import admin
from .models import WorkFlowAI

# Register your models here.

class WorkflowAIModelAdmin(admin.ModelAdmin):
    search_fields = ['country_name', 'currency_name', 'currency_code']

admin.site.register(WorkFlowAI,WorkflowAIModelAdmin)
