import os
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from .models import PPPCalculation
from .serializers import CurrencyNameSerializer
from .sendmail import send_mail
import currencyapicom
from dotenv import load_dotenv

load_dotenv()


currency_api_key = os.getenv("CURRENCY_API")

"""GET EXCHANGE RATE FROM CURRENCY API"""


# get the latest rate using the currency api
def get_latest_rate(from_currency, to_currency):
    print("called")
    client = currencyapicom.Client(currency_api_key)
    response = client.latest(f"{from_currency}", [f"{to_currency}"])
    print(response)
    try:
        result = response["data"][f"{to_currency}"]["value"]
        return result
    except:
        result = response["message"]
        return result



"""GET ALL CURRENCY NAME AND COUNTRY NAME"""

def get_all_currency_name():
    obj = PPPCalculation.objects.all()
    currency_name_list = []
    country_name_list = []
    for item in obj:
        if item.currency_name not in currency_name_list:
            currency_name_list.append(item.currency_name)
        if item.country_name not in country_name_list:
            country_name_list.append(item.country_name)

    currency_name_list.sort()
    country_name_list.sort()
    return Response(
        {
            "success": True,
            "message": "List of country and currency name",
            "currency": currency_name_list,
            "country": country_name_list,
        },
        status=status.HTTP_200_OK,
    )





"""CALCULATE THE PURCHASING POWER PARITY"""


def get_ppp_data(
    base_currency, base_price, base_country, target_country, target_currency,email
):
    # BASE COUNTRY
    # get base country object from the database base
    base_country_obj = PPPCalculation.objects.get(Q(country_name__iexact=base_country))
    base_country_currency_code = base_country_obj.currency_code
    base_world_bank_ppp = base_country_obj.world_bank_ppp

    # TARGET COUNTRY
    # get target country object from the database base
    target_country_obj = PPPCalculation.objects.get(
        Q(country_name__iexact=target_country)
    )

    target_country_world_bank_ppp = target_country_obj.world_bank_ppp
    target_country_currency_code = target_country_obj.currency_code
    

    try:
        # GET EXCHANGE RATE OF BASE COUNTRY IN BASE CURRENCY
        # get base curency object from the database by using the base currency as the filter
        base_currency_code = PPPCalculation.objects.filter(
            Q(currency_name__iexact=base_currency)
        )[0].currency_code.upper()

        res1 = get_latest_rate(base_currency_code, base_country_currency_code)
        try:
            base_currency_exchange_rate = res1 * float(base_price)
        except:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "details": f"{res1}",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # GET PPP RATIO
        world_bank_division = base_world_bank_ppp / target_country_world_bank_ppp
        purchasing_power = float(base_currency_exchange_rate) / world_bank_division

        # GET EXCHANGE RATE OF TARGET COUNTRY PPP RATIO IN TARGET CURRENCY
        # get target curency object from the database by using the target currency as the filter
        target_currency_code = PPPCalculation.objects.filter(
            Q(currency_name__iexact=target_currency)
        )[0].currency_code.upper()

        
        res2 = get_latest_rate(target_country_currency_code, target_currency_code)
        exchange_rate = get_latest_rate(base_currency_code,target_currency_code)
        print(base_currency_code,target_currency_code)
        print("exchange_rate",exchange_rate)
        try:
            target_currency_exchange_rate = res2 * (purchasing_power)
        except:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "details": f"{res1}",
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
    except Exception as e:
        return Response(
            {
                "success": False,
                "message": "something went wrong",
                "details": "Invalid Currency Name",
                "error": f"{e}",
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    email = email
    base_price_in_country = f"{base_price} {base_currency_code}"
    calculated_price_in_target_country = (
        f"{target_currency_exchange_rate:.2f} {target_currency_code}"
    )
    price_in_base_country = (
        f"{base_currency_exchange_rate:.2f} {base_country_currency_code}"
    )
    basecountry = base_country
    targetcountry = target_country
    target_price = f"{purchasing_power:.2f} {target_country_currency_code}"
    calculated_price_base_on_ppp = (
        f"{target_currency_exchange_rate:.2f} {target_currency_code}"
    )
    send_mail(
        email,
        base_currency,
        base_currency_code,
        target_currency,
        target_currency_code,
        base_price_in_country,
        calculated_price_in_target_country,
        price_in_base_country,
        basecountry,
        targetcountry,
        exchange_rate,
        target_price,
        calculated_price_base_on_ppp,
    )
    print("target_currency_code from helper",target_currency_code)
    return Response(
        {
            "success": True,
            "message": "Expected values",
            "email":email,
            "base_country": base_country,
            "target_country": target_country,
            "base_currency":base_currency,
            "target_currency":target_currency,
            "base_currency_code":base_currency_code,
            "target_currency_code":target_currency_code,
            f"base_price_in_{base_country}": f"{base_price} {base_currency_code}",
            f"calculated_price_in_{target_country}": f"{target_currency_exchange_rate:.2f} {target_currency_code}",
            "price_in_base_country": f"{base_currency_exchange_rate:.2f} {base_country_currency_code}",
            "exchange_rate":f"{exchange_rate:.4f}",
            "target_price": f"{purchasing_power:.2f} {target_country_currency_code}",
            "calculated_price_base_on_ppp": f"{target_currency_exchange_rate:.2f} {target_currency_code}",
        },
        status=status.HTTP_200_OK,
    )


# {
#             "success": True,
#             "message": "Expected values",
#             "base_currency_exchange_rate": f"{base_currency_exchange_rate} {base_country_currency_code}",
#             "purchasing_power": f"{purchasing_power} {target_country_currency_code}",
#             "target_currency_exchange_rate": f"{target_currency_exchange_rate} {target_currency_code}",
#         },


# def get_all_currency_name():
#     obj = PPPCalculation.objects.all()
#     currency_name_list = []
#     country_name_list = []
#     for item in obj:
#         if item.currency_name not in currency_name_list:
#             currency_name_list.append(item.currency_name)
#         if item.country_name not in country_name_list:
#             country_name_list.append(item.country_name)

#     currency_name_list.sort()
#     country_name_list.sort()
#     currency_name = []
#     country_name = []
#     for currency in currency_name_list:
#         currency_name.append({"currency_name": currency})
#     for country in country_name_list:
#         country_name.append({"country_name": country})
#     return Response(
#         {
#             "success": True,
#             "message": "List of country and currency name",
#             "currency_name": currency_name,
#             "country_name": country_name,
#         },
#         status=status.HTTP_200_OK,
#     )