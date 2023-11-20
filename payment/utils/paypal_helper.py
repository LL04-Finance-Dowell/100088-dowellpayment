import requests
import base64
import json
from rest_framework import status
from rest_framework.response import Response
from .qrcodes import payment_qrcode
from .sendmail import send_mail_one, send_mail_two


def processApikey(api_key):
    """API URL FOR DOWELL SERVICE"""
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
    paypal_url,
    template_id=None,
    voucher_code=None,
    generate_qrcode=None,
    api_key=None,
):
    if api_key:
        """CHECK IF API KEY IS VALID"""
        validate = processApikey(api_key)
        if validate["success"] == False:
            return Response(
                {"success": False, "message": validate["message"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    print(voucher_code)
    if price <= 0:
        return Response(
            {"success": False, "message": "price cant be zero or less than zero"},
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

    """INITIALIZE PAYPAL PAYMENT FOR USER"""
    response = requests.post(url, headers=headers, data=json.dumps(body)).json()
    if "name" in response and response["name"] == "UNPROCESSABLE_ENTITY":
        return Response(
            {
                "success": False,
                "error": response["name"],
                "details": response["details"][0]["description"],
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if "error" in response and response["error"] == "invalid_client":
        return Response(
            {
                "success": False,
                "error": response["error"],
                "details": response["error_description"],
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    try:
        payment_id = response["id"]
        """CONNECT TO DOWELL DATABASE AND STORE THE INFORMATION"""
        transaction_info = model_instance(
            payment_id, "", product_name, "", template_id, voucher_code
        )
    except Exception as e:
        return Response(
            {"success": False, "message": "something went wrong", "error": f"{e}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    approve_payment = response["links"][1]["href"]

    """GENERATE QRCODE FOR PAYMENT"""
    if generate_qrcode == True:
        logo_basewidth = 30
        data = payment_qrcode(approve_payment, payment_id, logo_basewidth)
        image_url = data["qr_image_url"]
        return Response(
            {
                "success": True,
                "approval_url": approve_payment,
                "qr_image_url": image_url,
                "payment_id": payment_id,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {
                "success": True,
                "approval_url": approve_payment,
                "payment_id": payment_id,
            },
            status=status.HTTP_200_OK,
        )


def verify_paypal(
    client_id,
    client_secret,
    payment_id,
    model_instance_update,
    model_instance_get,
    paypal_url,
    api_key=None,
):
    if api_key:
        """CHECK IF API KEY IS VALID"""
        validate = processApikey(api_key)
        if validate["success"] == False:
            return Response(
                {"success": False, "message": validate["message"]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
    url = f"{paypal_url}/v2/checkout/orders/{payment_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {encoded_auth.decode()}",
        "Prefer": "return=representation",
    }

    """GET PAYMENT DETAILS FROM PAYPAL USING THE PAYMENT ID"""
    response = requests.get(url, headers=headers).json()
    print(response)
    try:
        if response["name"] == "RESOURCE_NOT_FOUND":
            return Response(
                {"success": False, "message": response["details"][0]["issue"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        pass
    try:
        if response["error"] == "invalid_client":
            return Response(
                {"success": False, "message": response["error_description"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except:
        payment_status = response["status"]
        if payment_status == "APPROVED":
            """GET PAYMENT DATA FROM DOWELL CONNECTION USING THE PAYMENT ID"""
            transaction = model_instance_get(payment_id)
            try:
                payment_id = response["id"]
            except:
                payment_id = ""
            try:
                amount = response["purchase_units"][0]["amount"]["value"]
            except:
                amount = ""
            try:
                currency = response["purchase_units"][0]["amount"][
                    "currency_code"
                ].upper()
            except:
                currency = ""
            try:
                name = response["purchase_units"][0]["shipping"]["name"]["full_name"]
            except:
                name = ""
            try:
                email = response["payer"]["email_address"]
            except:
                email = ""
            try:
                city = response["purchase_units"][0]["shipping"]["address"][
                    "admin_area_2"
                ]
            except:
                city = ""

            try:
                state = response["purchase_units"][0]["shipping"]["address"][
                    "admin_area_1"
                ]
            except:
                state = ""
            try:
                address = response["purchase_units"][0]["shipping"]["address"][
                    "address_line_1"
                ]
            except:
                address = ""

            try:
                postal_code = response["purchase_units"][0]["shipping"]["address"][
                    "postal_code"
                ]
            except:
                postal_code = ""
            try:
                country_code = response["purchase_units"][0]["shipping"]["address"][
                    "country_code"
                ]
            except:
                country_code = ""
            try:
                date = response["create_time"].split("T")[0]
            except:
                date = ""
            order_id = payment_id
            payment_method = "Paypal"
            desc = transaction["data"]["desc"]
            ref_id = payment_id

            try:
                voucher_code = transaction["data"]["voucher_code"]
            except:
                voucher_code = ""

            mail_sent = transaction["data"]["mail_sent"]
            invoice_number = transaction["data"]["invoice_number"]
            order_number = transaction["data"]["order_number"]

            """USE THIS MAIL TEMPLATE IF VOUCHER CODE IS NOT INCLUDED IN THE PAYMENT DATA """
            if mail_sent == "True" and voucher_code == "":
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
                    invoice_number,
                    order_number,
                    payment_method,
                )

            """USE THIS MAIL TEMPLATE IF VOUCHER CODE IS INCLUDED IN THE PAYMENT DATA """
            if mail_sent == "True" and voucher_code != "":
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
                    invoice_number,
                    order_number,
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
                {"success": True, "status": "succeeded"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"success": False, "status": "failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
