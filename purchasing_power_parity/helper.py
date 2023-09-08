import os
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from .models import PPPCalculation
from .serializers import CurrencyNameSerializer
import currencyapicom
from dotenv import load_dotenv

load_dotenv()


currency_api_key = os.getenv("CURRENCY_API")

"""GET EXCHANGE RATE FROM CURRENCY API"""


def get_latest_rate(from_currency, to_currency):
    client = currencyapicom.Client(currency_api_key)
    response = client.latest(f"{from_currency}", [f"{to_currency}"])
    print(response)
    result = response["data"][f"{to_currency}"]["value"]
    return result


"""GET ALL CURRENCY NAME AND COUNTRY NAME"""


def get_all_currency_name():
    obj = PPPCalculation.objects.all()
    serializer = CurrencyNameSerializer(obj, many=True)
    return Response(
        {
            "success": True,
            "message": "List of country and currency name",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


"""CALCULATE THE PURCHASING POWER PARITY"""


def get_ppp_data(
    base_currency, base_price, base_country, target_country, target_currency
):
    # BASE COUNTRY
    base_country_obj = PPPCalculation.objects.get(Q(country_name__iexact=base_country))
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
        base_currency_code = PPPCalculation.objects.filter(
            Q(currency_name__iexact=base_currency)
        )[0].currency_code.upper()
        base_currency_exchange_rate = get_latest_rate(
            base_currency_code, base_country_currency_code
        ) * float(base_price)

        # GET PPP RATIO
        world_bank_division = base_world_bank_ppp / target_country_world_bank_ppp
        purchasing_power = float(base_currency_exchange_rate) / world_bank_division

        # GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
        target_currency_code = PPPCalculation.objects.filter(
            Q(currency_name__iexact=target_currency)
        )[0].currency_code.upper()
        target_currency_exchange_rate = get_latest_rate(
            target_country_currency_code, target_currency_code
        ) * (purchasing_power)

    except Exception as e:
        return Response(
            {
                "success": False,
                "message": "something went wrong",
                "details": "Invalid Currency Name",
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    return Response(
        {
            "success": True,
            "message": "Expected values",
            "base_currency_exchange_rate": f"{base_currency_exchange_rate} {base_country_currency_code}",
            "purchasing_power": f"{purchasing_power} {target_country_currency_code}",
            "target_currency_exchange_rate": f"{target_currency_exchange_rate} {target_currency_code}",
        },
        status=status.HTTP_200_OK,
    )
