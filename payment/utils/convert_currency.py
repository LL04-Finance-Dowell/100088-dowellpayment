# converter/utils.py
import requests
from dotenv import load_dotenv
load_dotenv()
import os
import currencyapicom
currency_api_key = os.getenv("CURRENCY_API")


# get the latest rate using the currency api
def get_latest_rate(from_currency, to_currency):
    print("called")
    print(from_currency)
    print(to_currency)
    client = currencyapicom.Client(currency_api_key)
    response = client.latest(f"{from_currency}", [f"{to_currency}"])
    print(response)
    print("goten response")
    try:
        result = response["data"][f"{to_currency}"]["value"]
        return result
    except:
        result = response["message"]
        return result



def convert_currency(amount, base_currency_code):
    to_currency_code = "USD"  # Assuming USD is the target currency code
    exchange_rate = get_latest_rate(base_currency_code.upper(), to_currency_code.upper())
    if exchange_rate is not None:
        converted_amount = amount * exchange_rate
        # Round the converted amount to two decimal places
        converted_amount_rounded = round(converted_amount, 2)
        return converted_amount_rounded

    return None


