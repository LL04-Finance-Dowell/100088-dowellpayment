from datetime import date
import uuid
import requests
import base64
import json
import stripe
from rest_framework import status
from rest_framework.response import Response
from .sendmail import send_mail
from django.shortcuts import get_object_or_404
from .serializers import (
    TransactionSerialiazer,
)


def processApikey(api_key):
    url = "https://100105.pythonanywhere.com/api/v1/process-api-key/"
    payload = {"api_key": api_key, "api_service_id": "DOWELL100012"}

    response = requests.post(url, json=payload)
    print(response.json())
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
        try:
            if validate["success"] == False:
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )

            elif validate["message"] == "Limit exceeded":
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )

            elif validate["message"] == "API key is inactive":
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {"message": f"api_service_id: {validate['api_service_id']}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    print("yes")
    if price <= 0:
        return Response(
            {"message": "price cant be zero or less than zero"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
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

    print(response)
    try:
        transaction_info = model_instance.objects.create(
            payment_id=response["id"], desc=product_name
        )
    except:
        return Response({"name": response["name"], "details": response["details"]})
    approve_payment = response["links"][1]["href"]
    return Response({"approval_url": approve_payment, "payment_id": response["id"]})


def verify_paypal(client_id, client_secret, payment_id, model_instance, api_key=None):
    if api_key:
        validate = processApikey(api_key)
        try:
            if validate["success"] == False:
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )

            elif validate["message"] == "Limit exceeded":
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )

            elif validate["message"] == "API key is inactive":
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {"message": f"api_service_id: {validate['api_service_id']}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
    url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{payment_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_auth.decode()}",
        "Prefer": "return=representation",
    }
    response = requests.get(url, headers=headers).json()
    print(response)
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
            transaction = get_object_or_404(model_instance, payment_id=payment_id)
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
            desc = transaction.desc

            if transaction.mail_sent == False:
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

            transaction.amount = amount
            transaction.currency = currency
            transaction.name = name
            transaction.email = email
            transaction.city = city
            transaction.state = state
            transaction.date = date
            transaction.address = address
            transaction.postal_code = postal_code
            transaction.country_code = country_code
            transaction.order_id = payment_id
            transaction.status = "succeeded"
            transaction.mail_sent = True
            transaction.save()

            serializer = TransactionSerialiazer(transaction)

            return Response(
                {"status": "succeeded", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"status": "failed"})
