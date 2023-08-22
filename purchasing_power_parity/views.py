from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PPPCalculation

# Create your views here.

# the start points are Dowell PPP (base country, base price, base currency, Target country,  target currency)
# Ex- dowell PPP (USA, 1, USD, India, INR)
# process find the equivalent price in India in INR for 1USD in USA
# End point [target price ()]


class GetPurchasingPowerParity(APIView):
    def post(self, request):
        data = request.data
        base_country = data["base_country"]
        base_price = data["base_price"]
        base_currency = data["base_currency"]
        target_country = data["target_country"]
        target_currency = data["target_currency"]
        
        #GET PPP OBJECT FROM DB

        #BASE COUNTRY
        base_country_currency_code = "USD"
        
        #BASE CURRENCY
        base_currency_obj = PPPCalculation.objects.get(currency_code=base_currency)
        base_world_bank_ppp = base_currency_obj.world_bank_ppp
        
        #TARGET COUNTRY
        target_country_obj = PPPCalculation.objects.get(country_name=target_country)
        target_country_world_bank_ppp = target_country_obj.world_bank_ppp
        target_country_currency = target_country_obj.currency_code
        
        #GET EXCHANGE RATE OF BASE CURRENCY IN BASE COUNTRY
        base_currency_obj = PPPCalculation.objects.get(currency_code=base_currency)
        base_currency_exchange_rate = base_currency_obj.usd_exchange_rate
        base_currency_code = base_currency_obj.currency_code

        #GET PPP RATIO
        world_bank_division = base_world_bank_ppp / target_country_world_bank_ppp
        purchasing_power = float(base_currency_exchange_rate) / world_bank_division


        #GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
        target_exchange_rate=target_country_obj.usd_exchange_rate


        

        print("base price", base_price)
        print("base_world_bank_ppp",base_world_bank_ppp)
        print("target_country_world_bank_ppp",target_country_world_bank_ppp)
         
        

        return Response(
            {"base_currency_exchange_rate":f"{base_price} {base_country_currency_code} = {base_currency_exchange_rate} {base_currency_code}","purchasing_power": f"{purchasing_power} {target_country_currency}",
             "target_currency_exchange_rate":f"{purchasing_power} {target_country_currency} = {base_currency_exchange_rate} {target_currency}"},
            status=status.HTTP_200_OK,
        )
