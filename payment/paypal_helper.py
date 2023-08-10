import requests
import base64
import json
from rest_framework import status
from rest_framework.response import Response
from .sendmail import send_mail
import os
from dotenv import load_dotenv

load_dotenv()

paypal_mode = os.getenv("LIVE_MODE", None)
if paypal_mode == "True":
    paypal_url = "https://api-m.paypal.com"
else:
    paypal_url = "https://api-m.sandbox.paypal.com"


def processApikey(api_key):
    url = f"https://100105.pythonanywhere.com/api/v3/process-services/?type=api_service&api_key={api_key}"
    payload = {"service_id": "DOWELL10006"}

    response = requests.post(url, json=payload)
    return response.json()


def paypal_payment(
    price,
    product_name,
    currency_code,
    callback_url,
    client_id,
    client_secret,
    model_instance,
    api_key=None,
):
    if api_key:
        validate = processApikey(api_key)
        if validate["success"] == False:
            return Response(
                {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
            )

    if price <= 0:
        return Response(
            {"message": "price cant be zero or less than zero"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
    url = f"{paypal_url}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_auth.decode()}",
        "Prefer": "return=representation",
    }
    body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": f"{currency_code.upper()}",
                    "value": f"{price}",
                }
            }
        ],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "payment_method_selected": "PAYPAL",
                    "locale": "en-US",
                    "landing_page": "LOGIN",
                    "user_action": "PAY_NOW",
                    "return_url": f"{callback_url}",
                    "cancel_url": f"{callback_url}",
                }
            }
        },
    }

    response = requests.post(url, headers=headers, data=json.dumps(body)).json()
    try:
        transaction_info = model_instance(response["id"], "", product_name, "")
    except:
        try:
            return Response(
                {"name": response["name"], "details": response["details"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except:
            return Response(
                {"error": response["error"], "details": response["error_description"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    approve_payment = response["links"][1]["href"]
    return Response(
        {"approval_url": approve_payment, "payment_id": response["id"]},
        status=status.HTTP_200_OK,
    )


def verify_paypal(
    client_id,
    client_secret,
    payment_id,
    model_instance_update,
    model_instance_get,
    api_key=None,
):
    if api_key:
        validate = processApikey(api_key)
        if validate["success"] == False:
            return Response(
                {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
            )

    encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
    url = f"{paypal_url}/v2/checkout/orders/{payment_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_auth.decode()}",
        "Prefer": "return=representation",
    }
    response = requests.get(url, headers=headers).json()
    try:
        if response["name"] == "RESOURCE_NOT_FOUND":
            return Response(
                {"message": response["details"][0]["issue"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        pass
    try:
        if response["error"] == "invalid_client":
            return Response(
                {"message": response["error_description"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        payment_status = response["status"]
        if payment_status == "APPROVED":
            transaction = model_instance_get(payment_id)
            payment_id = response["id"]
            amount = response["purchase_units"][0]["amount"]["value"]
            currency = response["purchase_units"][0]["amount"]["currency_code"].upper()
            name = response["purchase_units"][0]["shipping"]["name"]["full_name"]
            email = response["payer"]["email_address"]
            city = response["purchase_units"][0]["shipping"]["address"]["admin_area_2"]
            state = response["purchase_units"][0]["shipping"]["address"]["admin_area_1"]
            address = response["purchase_units"][0]["shipping"]["address"][
                "address_line_1"
            ]
            postal_code = response["purchase_units"][0]["shipping"]["address"][
                "postal_code"
            ]
            country_code = response["purchase_units"][0]["shipping"]["address"][
                "country_code"
            ]
            date = response["create_time"].split("T")[0]
            order_id = payment_id
            payment_method = "Paypal"
            desc = transaction["data"]["desc"]

            mail_sent = transaction["data"]["mail_sent"]
            if mail_sent == "False":
                res = send_mail(
                    amount,
                    currency,
                    name,
                    email,
                    desc,
                    date,
                    city,
                    address,
                    postal_code,
                    order_id,
                    payment_method,
                )
            transaction_update = model_instance_update(
                payment_id,
                amount,
                currency,
                name,
                email,
                city,
                state,
                address,
                postal_code,
                country_code,
            )

            return Response(
                {
                    "status": "succeeded",
                    "data": {
                        "payment_id": f"{payment_id}",
                        "amount": f"{amount}",
                        "currency": f"{currency}",
                        "name": f"{name}",
                        "email": f"{email}",
                        "desc": f"{desc}",
                        "date": f"{date}",
                        "city": f"{city}",
                        "state": f"{state}",
                        "address": f"{address}",
                        "postal_code": f"{postal_code}",
                        "country_code": f"{country_code}",
                        "status": "succeeded",
                        "mail_sent": "true",
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"status": "failed"})
