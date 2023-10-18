from datetime import date
import uuid
import requests
import stripe
from rest_framework import status
from rest_framework.response import Response
from decimal import Decimal, ROUND_HALF_UP
from .qrcodes import payment_qrcode
from .sendmail import send_mail_one, send_mail_two


def processApikey(api_key):
    url = f"https://100105.pythonanywhere.com/api/v3/process-services/?type=api_service&api_key={api_key}"
    payload = {"service_id": "DOWELL10006"}

    response = requests.post(url, json=payload)
    return response.json()


def stripe_payment(
    price,
    product,
    currency_code,
    callback_url,
    stripe_key,
    model_instance,
    template_id=None,
    voucher_code=None,
    generate_qrcode=None,
    api_key=None,
):
    print(generate_qrcode)
    if api_key:
        """CHECK IF API KEY IS VALID"""
        validate = processApikey(api_key)
        print(validate)
        if validate["success"] == False:
            return Response(
                {"success": False, "message": validate["message"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    stripe.api_key = stripe_key
    today = date.today()
    unique_id = uuid.uuid4()
    payment_id = str(unique_id)

    # convert the price to Decimal type
    price_decimal = Decimal(price)

    print("price_decimal", price_decimal)
    # make sure the price retains is decimal value
    rounded_price = price_decimal.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    # convert the price to cent
    price_in_cents = int(rounded_price * 100)
    # price_in_cents = 14566

    print("price_in_cents", price_in_cents)
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": f"{currency_code.lower()}",
                    "product_data": {
                        "name": f"{product}",
                    },
                    # "unit_amount": f"{(price) * 100}",
                    "unit_amount": f"{price_in_cents}",
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

    """CONNECT TO DOWELL DATABASE AND STORE THE INFORMATION"""
    transaction_info = model_instance(
        payment_id, session.id, product, today, template_id, voucher_code
    )

    # print(transaction_info)

    if generate_qrcode == True:
        logo_basewidth = 50
        data = payment_qrcode(session.url, payment_id, logo_basewidth)
        image_url = data["qr_image_url"]
        return Response(
            {
                "success": True,
                "approval_url": f"{session.url}",
                "qr_image_url": image_url,
                "payment_id": payment_id,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "success": True,
                "approval_url": f"{session.url}",
                "payment_id": payment_id,
            },
            status=status.HTTP_200_OK,
        )


def verify_stripe(
    stripe_key, payment_id, model_instance_update, model_instance_get, api_key=None
):
    if api_key:
        validate = processApikey(api_key)
        print(validate)
        if validate["success"] == False:
            return Response(
                {"success": False, "message": validate["message"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    stripe.api_key = stripe_key

    """GET PAYMENT DATA FROM DOWELL CONNECTION USING THE PAYMENT ID"""
    transaction = model_instance_get(payment_id)
    session_id = transaction["data"]["session_id"]

    """GET PAYMENT DETAILS FROM STRIPE USING THE SESSION ID"""
    payment_session = stripe.checkout.Session.retrieve(session_id)
    print(payment_session)
    payment_status = payment_session["payment_status"]
    state = payment_session["status"]

    # Check the payment status
    if payment_status == "paid" and state == "complete":
        try:
            amount = payment_session["amount_total"] / 100
        except:
            amount = ""
        try:
            currency = payment_session["currency"].upper()
        except:
            currency = ""
        try:
            name = payment_session["customer_details"]["name"]
        except:
            name = ""
        try:
            email = payment_session["customer_details"]["email"]
        except:
            email = ""
        try:
            city = payment_session["customer_details"]["address"]["city"]
        except:
            city = ""
        try:
            state = payment_session["customer_details"]["address"]["state"]
        except:
            state = ""
        try:
            address = payment_session["customer_details"]["address"]["line1"]
        except:
            address = ""
        try:
            postal_code = payment_session["customer_details"]["address"]["postal_code"]
        except:
            postal_code = ""
        try:
            country_code = payment_session["customer_details"]["address"]["country"]
        except:
            country_code = ""
        try:
            ref_id = payment_session["payment_intent"]
        except:
            ref_id = ""
        desc = transaction["data"]["desc"]
        date = transaction["data"]["date"]

        payment_method = "Stripe"

        mail_sent = transaction["data"]["mail_sent"]

        try:
            voucher_code = transaction["data"]["voucher_code"]
        except:
            voucher_code = ""

        """USE THIS MAIL TEMPLATE IF VOUCHER CODE IS NOT INCLUDED IN THE PAYMENT DATA """
        if mail_sent == "False" and voucher_code == "":
            res = send_mail_one(
                amount,
                currency,
                name,
                email,
                desc,
                date,
                city,
                address,
                postal_code,
                ref_id,
                payment_method,
            )

        """USE THIS MAIL TEMPLATE IF VOUCHER CODE IS INCLUDED IN THE PAYMENT DATA """
        if mail_sent == "False" and voucher_code != "":
            res = send_mail_two(
                amount,
                currency,
                name,
                email,
                desc,
                date,
                city,
                address,
                postal_code,
                voucher_code,
                ref_id,
                payment_method,
            )
        """CONNECT TO DOWELL DATABASE AND UPDATE THE PAYMENT DETAILS"""
        transaction_update = model_instance_update(
            payment_id,
            ref_id,
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
                "success": True,
                "status": "succeeded",
            },
            status=status.HTTP_200_OK,
        )
    elif (
        payment_status == "unpaid"
        and state == "open"
        or payment_status == "unpaid"
        and state == "expired"
    ):
        return Response(
            {"success": False, "status": "failed"}, status=status.HTTP_401_UNAUTHORIZED
        )
    else:
        return Response(
            {"success": False, "message": "something went wrong"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
