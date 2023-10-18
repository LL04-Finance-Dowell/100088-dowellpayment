import requests


def generate_voucher(timezone, description, credit):
    headers = {"content-type": "application/json"}
    url = " https://100105.pythonanywhere.com/api/v3/public-voucher/?type=generate_public_voucher"

    data = {"timezone": timezone, "description": description, "credit": credit}

    response = requests.post(url, json=data, headers=headers).json()
    return response
