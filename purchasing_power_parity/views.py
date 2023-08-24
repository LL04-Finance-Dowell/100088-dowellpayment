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

# the start points are Dowell PPP (base currency, base price, base country, Target country,  target currency)
# Ex- dowell PPP (USD, 1, Nigeria, India, INR)
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
            base_currency = data["base_currency"].upper()
            base_price = data["base_price"]
            base_country = data["base_country"]
            target_country = data["target_country"]
            target_currency = data["target_currency"].upper()

            # GET PPP OBJECT FROM DB

            # BASE COUNTRY
            base_country_obj = PPPCalculation.objects.get(
                Q(country_name__iexact=base_country)
            )
            base_country_currency_code = base_country_obj.currency_code
            base_world_bank_ppp = base_country_obj.world_bank_ppp

            # TARGET COUNTRY
            target_country_obj = PPPCalculation.objects.get(
                Q(country_name__iexact=target_country)
            )
            target_country_world_bank_ppp = target_country_obj.world_bank_ppp
            target_country_currency_code = target_country_obj.currency_code

            try:
                # GET EXCHANGE RATE OF BASE COUNTRY IN BASE CURRENCY
                base_currency_exchange_rate = get_latest_rate(
                    base_currency, base_country_currency_code
                ) * float(base_price)

                # GET PPP RATIO
                world_bank_division = (
                    base_world_bank_ppp / target_country_world_bank_ppp
                )
                purchasing_power = (
                    float(base_currency_exchange_rate) / world_bank_division
                )

                # GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
                target_currency_exchange_rate = get_latest_rate(
                    target_country_currency_code, target_currency
                ) * (purchasing_power)

            except Exception as e:
                return Response(
                    {
                        "message": "something went wrong",
                        "details": "Invalid Currency Code",
                        "error": f"{e}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "base_currency_exchange_rate": f"{base_price} {base_currency} = {base_currency_exchange_rate} {base_country_currency_code}",
                    "purchasing_power": f"{base_currency_exchange_rate} {base_country_currency_code} = {purchasing_power} {target_country_currency_code}",
                    "target_currency_exchange_rate": f"{purchasing_power} {target_country_currency_code} = {target_currency_exchange_rate} {target_currency}",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "message": "something went wrong",
                    "details": "Invalid Country Name",
                    "error": f"{e}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
