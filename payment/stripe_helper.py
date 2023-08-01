from datetime import date
import uuid
import requests
import stripe
from rest_framework import status
from rest_framework.response import Response
from .sendmail import send_mail


def processApikey(api_key):
    url = "https://100105.pythonanywhere.com/api/v1/process-api-key/"
    payload = {"api_key": api_key, "api_service_id": "DOWELL100012"}

    response = requests.post(url, json=payload)
    print(response.json())
    return response.json()


def stripe_payment(
    price,
    product,
    currency_code,
    callback_url,
    stripe_key,
    model_instance,
    api_key=None,
):
    if api_key:
        validate = processApikey(api_key)
        print(validate)
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
    stripe.api_key = stripe_key
    today = date.today()
    unique_id = uuid.uuid4()
    payment_id = str(unique_id)

    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": f"{currency_code.lower()}",
                    "product_data": {
                        "name": f"{product}",
                    },
                    "unit_amount": f"{(price) * 100}",
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"{callback_url}?token={payment_id}",
        cancel_url=f"{callback_url}?token={payment_id}",
        billing_address_collection="required",
        payment_intent_data={
            "metadata": {
                "description": f"{product}",
                "payment_id": payment_id,
                "date": today,
            }
        },
    )

    transaction_info = model_instance(payment_id, session.id, product, today)
    print(transaction_info)
    return Response(
        {"approval_url": f"{session.url}", "payment_id": payment_id},
        status=status.HTTP_200_OK,
    )


def verify_stripe(
    stripe_key, payment_id, model_instance_update, model_instance_get, api_key=None
):
    if api_key:
        validate = processApikey(api_key)
        print(validate)
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
    stripe.api_key = stripe_key
    transaction = model_instance_get(payment_id)
    session_id = transaction["data"]["session_id"]
    payment_session = stripe.checkout.Session.retrieve(session_id)
    print(payment_session)
    payment_status = payment_session["payment_status"]

    # Check the payment status
    if payment_status == "paid":
        amount = payment_session["amount_total"] / 100
        currency = payment_session["currency"].upper()
        name = payment_session["customer_details"]["name"]
        email = payment_session["customer_details"]["email"]
        city = payment_session["customer_details"]["address"]["city"]
        state = payment_session["customer_details"]["address"]["state"]
        address = payment_session["customer_details"]["address"]["line1"]
        postal_code = payment_session["customer_details"]["address"]["postal_code"]
        country_code = payment_session["customer_details"]["address"]["country"]
        desc = transaction["data"]["desc"]
        date = transaction["data"]["date"]
        order_id = payment_id
        payment_method = "Stripe"

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
    elif payment_status == "unpaid":
        # Payment isgenerate pending or failed
        return Response({"status": "failed"}, status=status.HTTP_200_OK)
    else:
        # Payment status is unknown or not found
        return Response({"message": "something went wrong"}, status=status.HTTP_200_OK)
