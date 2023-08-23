from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PPPCalculation
import requests
import os
from dotenv import load_dotenv
import json
from django.db.models import Q

import currencyapicom

load_dotenv()

currency_api_key = os.getenv("CURRENCY_API")

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
        '''use base country data to get the base country currency code'''
        base_country_obj = PPPCalculation.objects.get(Q(country_name__iexact=base_country))
        base_country_currency_code = base_country_obj.currency_code
        
        #BASE CURRENCY
        '''get the base currency world bank ppp from db'''
        base_currency_obj = PPPCalculation.objects.get(Q(currency_code__iexact=base_currency))
        base_world_bank_ppp = base_currency_obj.world_bank_ppp
        
        #TARGET COUNTRY
        '''get the target country world bank ppp from db'''
        target_country_obj = PPPCalculation.objects.get(Q(country_name__iexact=target_country))
        target_country_world_bank_ppp = target_country_obj.world_bank_ppp
        target_country_currency = target_country_obj.currency_code
        
        #GET EXCHANGE RATE OF BASE CURRENCY IN BASE COUNTRY
        '''
        get the exchange rate of the base currency using the base country data
        This exchange rate will be gotten from an external API
        '''
        base_currency_obj = PPPCalculation.objects.get(Q(currency_code__iexact=base_currency))
        # base_currency_exchange_rate = base_currency_obj.usd_exchange_rate * float(base_price)
        base_currency_code = base_currency_obj.currency_code
        client = currencyapicom.Client('currency_api_key')
        result = client.latest(f"{base_country_currency_code}",[f"{base_currency_code}"])
        print("result 1")
        print(result)
        base_currency_exchange_rate = result["data"][f"{base_currency_code}"]["value"] * float(base_price)
        print(base_currency_exchange_rate)

        # out = get_latest_rate("EUR","NGN")
        # print("out",out)

        
       


        #GET PPP RATIO
        world_bank_division = base_world_bank_ppp / target_country_world_bank_ppp
        purchasing_power = float(base_currency_exchange_rate) / world_bank_division


        #GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
        '''
        get the exchange rate of target country ppp ratio in target currency from an
        external API
        '''
        # target_exchange_rate=target_country_obj.usd_exchange_rate
        # target_currency_exchange_rate = purchasing_power/target_exchange_rate

        client = currencyapicom.Client('currency_api_key')
        result2 = client.latest(f"{target_country_currency}",[f"{target_currency}"])
        print("result 2")
        print(result2)
        target_currency_exchange_rate = result2["data"][f"{target_currency}"]["value"] * (purchasing_power)
        print(target_currency_exchange_rate)


        

        # print("base price", base_price)
        # print("base_world_bank_ppp",base_world_bank_ppp)
        # print("target_country_world_bank_ppp",target_country_world_bank_ppp)
         
        

        return Response(
            {"base_currency_exchange_rate":f"{base_price} {base_country_currency_code} = {base_currency_exchange_rate} {base_currency_code}","purchasing_power": f"{base_currency_exchange_rate} {base_currency_code} = {purchasing_power} {target_country_currency}",
             "target_currency_exchange_rate":f"{purchasing_power} {target_country_currency} = {target_currency_exchange_rate} {target_currency}"},
            status=status.HTTP_200_OK,
        )
