from django.contrib import admin
from .models import (ExchangeRate,WorkFlowAI,WifiQrcode,DigitalQ,
LogoScan,Nps,Voc,UxLive,SocialMediaAutomation,LicenseCompatibility)

# Register your models here.

class WorkflowAIModelAdmin(admin.ModelAdmin):
    search_fields = ['country_name', 'currency_name', 'currency_code']

admin.site.register(ExchangeRate)

admin.site.register(WorkFlowAI,WorkflowAIModelAdmin)
admin.site.register(WifiQrcode)
admin.site.register(DigitalQ)
admin.site.register(LogoScan)
admin.site.register(Nps)
admin.site.register(Voc)
admin.site.register(UxLive)
admin.site.register(SocialMediaAutomation)
admin.site.register(LicenseCompatibility)
