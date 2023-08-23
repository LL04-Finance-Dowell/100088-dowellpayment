import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PPPCalculation
from dotenv import load_dotenv
from django.db.models import Q

import currencyapicom

load_dotenv()

currency_api_key = os.getenv("CURRENCY_API")

# Create your views here.

# the start points are Dowell PPP (base country, base price, base currency, Target country,  target currency)
# Ex- dowell PPP (USA, 1, USD, India, INR)
# process find the equivalent price in India in INR for 1USD in USA
# End point [target price ()]


def get_latest_rate(from_currency, to_currency):
    client = currencyapicom.Client(currency_api_key)
    response = client.latest(f"{from_currency}", [f"{to_currency}"])
    print(response)
    result = response["data"][f"{to_currency}"]["value"]
    return result


class GetPurchasingPowerParity(APIView):
    def post(self, request):
        try:
            data = request.data
            base_country = data["base_country"]
            base_price = data["base_price"]
            base_currency = data["base_currency"]
            target_country = data["target_country"]
            target_currency = data["target_currency"]

            # GET PPP OBJECT FROM DB

            # BASE COUNTRY
            """use base country data to get the base country currency code"""
            base_country_obj = PPPCalculation.objects.get(
                Q(country_name__iexact=base_country)
            )
            base_country_currency_code = base_country_obj.currency_code

            # BASE CURRENCY
            """get the base currency world bank ppp from db"""
            base_currency_obj = PPPCalculation.objects.get(
                Q(currency_code__iexact=base_currency)
            )
            base_world_bank_ppp = base_currency_obj.world_bank_ppp

            # TARGET COUNTRY
            """get the target country world bank ppp from db"""
            target_country_obj = PPPCalculation.objects.get(
                Q(country_name__iexact=target_country)
            )
            target_country_world_bank_ppp = target_country_obj.world_bank_ppp
            target_country_currency = target_country_obj.currency_code

            # GET EXCHANGE RATE OF BASE CURRENCY IN BASE COUNTRY
            """
            get the exchange rate of the base currency using the base country data
            This exchange rate will be gotten from an external API
            """
            base_currency_obj = PPPCalculation.objects.get(
                Q(currency_code__iexact=base_currency)
            )
            base_currency_code = base_currency_obj.currency_code

        except Exception as e:
            return Response(
                {
                    "message": "something went wrong",
                    "details": "currency code or country name not correct",
                    "error": f"{e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            base_currency_exchange_rate = get_latest_rate(
                base_country_currency_code, base_currency_code
            ) * float(base_price)

            # GET PPP RATIO
            world_bank_division = base_world_bank_ppp / target_country_world_bank_ppp
            purchasing_power = float(base_currency_exchange_rate) / world_bank_division

            # GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
            """
            get the exchange rate of target country ppp ratio in target currency from an
            external API
            """
            target_currency_exchange_rate = get_latest_rate(
                target_country_currency, target_currency
            ) * (purchasing_power)

        except Exception as e:
            return Response(
                {
                    "message": "something went wrong",
                    "details": "currency code not correct",
                    "error": f"{e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "base_currency_exchange_rate": f"{base_price} {base_country_currency_code} = {base_currency_exchange_rate} {base_currency_code}",
                "purchasing_power": f"{base_currency_exchange_rate} {base_currency_code} = {purchasing_power} {target_country_currency}",
                "target_currency_exchange_rate": f"{purchasing_power} {target_country_currency} = {target_currency_exchange_rate} {target_currency}",
            },
            status=status.HTTP_200_OK,
        )
