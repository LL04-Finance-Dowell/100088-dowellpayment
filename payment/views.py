from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import ExchangeRate, TransactionDetail, PaymentLinkTransaction
from .serializers import (
    PaymentSerializer,
    PaypalPaymentLinkSerializer,
    StripePaymentLinkSerializer,
    TransactionSerialiazer,
)
from .supported_currency import stripe_supported_currency, paypal_supported_currency
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404
from .sendmail import send_mail
from datetime import date

import os
import json
import requests
import base64
import stripe
import uuid
from dotenv import load_dotenv
import paypalrestsdk

load_dotenv()


stripe_key = os.getenv("STRIPE_KEY", None)
client_id = os.getenv("PAYPAL_CLIENT_ID", None)
client_secret = os.getenv("PAYPAL_SECRET_KEY", None)


class Success(View):
    template_name = "payment/success.html"

    def get(self, request):
        return render(request, self.template_name)


class Error(View):
    template_name = "payment/error.html"

    def get(self, request):
        return render(request, self.template_name)


def processApikey(api_key):
    url = "https://100105.pythonanywhere.com/api/v1/process-api-key/"
    payload = {"api_key": api_key, "api_service_id": "DOWELL100012"}

    response = requests.post(url, json=payload)
    print(response.json())
    return response.json()


class StripePayment(APIView):
    stripe.api_key = stripe_key

    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
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

        try:
            today = date.today()
            data = request.data
            price = data["price"]
            product = data["product"]
            currency_code = data["currency_code"]
            callback_url = data["callback_url"]

            exchange_rate_obj = ExchangeRate.objects.filter(
                currency_code__iexact=currency_code
            )

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response(
                    {"message": f" {currency_code}, not a valid currency code."}
                )

            converted_price = price / usd_rate
            if int(price) < 1:
                return Response(
                    {
                        "message": f"The price cannot be {price}, the lowest number acceptable is 1."
                    }
                )

            if converted_price < 0.5:
                return Response(
                    {
                        "message": f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"
                    }
                )

            try:
                # try if the currency is supported by stripe
                session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            "price_data": {
                                "currency": f"{currency_code.lower()}",
                                "product_data": {
                                    "name": f"{product}",
                                },
                                "unit_amount": f"{int(price) * 100}",
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="payment",
                    success_url=f"{callback_url}",
                    cancel_url=f"{callback_url}",
                    billing_address_collection="required",
                    payment_intent_data={
                        "metadata": {
                            "description": f"{product}",
                            "payment_id": payment_id,
                            "date": today,
                        }
                    },
                )
                transaction_info = TransactionDetail.objects.create(
                    payment_id=payment_id,
                    session_id=session.id,
                    desc=product,
                    date=today,
                )
                return Response(
                    {"approval_url": f"{session.url}", "payment_id": payment_id},
                    status=status.HTTP_200_OK,
                )

            except:
                # If the currency is not supported by stripe, convert it to usd before processing.
                session = stripe.checkout.Session.create(
                    line_items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {
                                    "name": f"{product}",
                                },
                                "unit_amount": f"{int(converted_price)*100}",
                            },
                            "quantity": 1,
                        }
                    ],
                    mode="payment",
                    success_url=f"{callback_url}",
                    cancel_url=f"{callback_url}",
                    billing_address_collection="required",
                    payment_intent_data={
                        "metadata": {
                            "description": f"{product}",
                            "payment_id": payement_id,
                            "date": today,
                        }
                    },
                )
                transaction_info = TransactionDetail.objects.create(
                    payment_id=payment_id,
                    session_id=session.id,
                    desc=product,
                    date=today,
                )
                return Response(
                    {"approval_url": f"{session.url}", "payment_id": payment_id},
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyStripePayment(APIView):
    def post(self, request, api_key):
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

        try:
            data = request.data
            payment_id = data["id"]
            transaction = get_object_or_404(TransactionDetail, payment_id=payment_id)
            payment_session = stripe.checkout.Session.retrieve(transaction.session_id)
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
                postal_code = payment_session["customer_details"]["address"][
                    "postal_code"
                ]
                country_code = payment_session["customer_details"]["address"]["country"]
                desc = transaction.desc
                date = transaction.date
                order_id = payment_id
                payment_method = "Stripe"

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
            elif payment_status == "unpaid":
                # Payment isgenerate pending or failed
                return Response({"status": "failed"}, status=status.HTTP_200_OK)
            else:
                # Payment status is unknown or not found
                return Response(
                    {"message": "something went wrong"}, status=status.HTTP_200_OK
                )

        except Http404:
            return JsonResponse(
                {"status": "error", "message": "Transaction not found"}, status=404
            )


class GenerateStripePaymentLink(APIView):
    def post(self, request, api_key):
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

        try:
            today = date.today()
            data = request.data
            stripe_key = data["stripe_key"]
            price = data["price"]
            product_name = data["product"]
            currency_code = data["currency_code"]
            callback_url = data["callback_url"]
            stripe.api_key = stripe_key
            exchange_rate_obj = ExchangeRate.objects.filter(
                currency_code__iexact=currency_code
            )

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response(
                    {"message": f" {currency_code}, not a valid currency code."}
                )

            converted_price = price / usd_rate
            if int(price) < 1:
                return Response(
                    {
                        "message": f"The price cannot be {price}, the lowest number acceptable is 1."
                    }
                )

            if converted_price < 0.5:
                return Response(
                    {
                        "message": f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"
                    }
                )

            try:
                product = stripe.Product.create(name=f"{product_name}")
                product_price = stripe.Price.create(
                    unit_amount=int(price) * 100,
                    currency=f"{currency_code.lower()}",
                    product=f"{product.id}",
                )

                payment_link = stripe.PaymentLink.create(
                    line_items=[{"price": f"{product_price.id}", "quantity": 1}],
                    billing_address_collection="required",
                    after_completion={
                        "type": "redirect",
                        "redirect": {
                            "url": f"{callback_url}"
                            + "?session_id={CHECKOUT_SESSION_ID}"
                        },
                    },
                )

                print(payment_link)
                return Response(
                    {"payment_link": payment_link.url}, status=status.HTTP_200_OK
                )
            except:
                product = stripe.Product.create(name=f"{product_name}")
                product_price = stripe.Price.create(
                    unit_amount=int(converted_price) * 100,
                    currency="usd",
                    product=f"{product.id}",
                )

                payment_link = stripe.PaymentLink.create(
                    line_items=[{"price": f"{product_price.id}", "quantity": 1}],
                    billing_address_collection="required",
                    after_completion={
                        "type": "redirect",
                        "redirect": {
                            "url": f"{callback_url}"
                            + "?session_id={CHECKOUT_SESSION_ID}"
                        },
                    },
                )

                print(payment_link)
                return Response(
                    {"payment_link": payment_link.url}, status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyStripePaymentLink(APIView):
    def post(self, request, api_key):
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

        try:
            today = date.today()
            data = request.data
            session_id = data["id"]
            payment_session = stripe.checkout.Session.retrieve(session_id)
            payment_status = payment_session["payment_status"]
            print(payment_session)

            # Verify payment link status
            if payment_status == "paid":
                check_payment_link = PaymentLinkTransaction.objects.filter(
                    session_id=session_id
                )
                if check_payment_link:
                    serializer = TransactionSerialiazer(check_payment_link[0])
                    return Response(
                        {"status": "succeeded", "data": serializer.data},
                        status=status.HTTP_200_OK,
                    )

                payment_id = payment_session["payment_intent"]
                amount = payment_session["amount_total"] / 100
                currency = payment_session["currency"].upper()
                name = payment_session["customer_details"]["name"]
                email = payment_session["customer_details"]["email"]
                city = payment_session["customer_details"]["address"]["city"]
                state = payment_session["customer_details"]["address"]["state"]
                address = payment_session["customer_details"]["address"]["line1"]
                postal_code = payment_session["customer_details"]["address"][
                    "postal_code"
                ]
                country_code = payment_session["customer_details"]["address"]["country"]
                order_id = payment_id
                payment_method = "Stripe"
                desc = "Order details"

                res = send_mail(
                    amount,
                    currency,
                    name,
                    email,
                    desc,
                    today,
                    city,
                    address,
                    postal_code,
                    order_id,
                    payment_method,
                )

                payment_link = PaymentLinkTransaction.objects.create(
                    payment_id=payment_id,
                    session_id=session_id,
                    amount=amount,
                    currency=currency,
                    name=name,
                    email=email,
                    desc=desc,
                    date=today,
                    city=city,
                    state=state,
                    address=address,
                    postal_code=postal_code,
                    mail_sent=True,
                    country_code=country_code,
                    order_id=payment_id,
                    status="succeeded",
                )

                serializer = TransactionSerialiazer(payment_link)

                # Payment link has been paid
                return Response(
                    {"status": "succeeded", "data": serializer.data},
                    status=status.HTTP_200_OK,
                )
            elif payment_status == "unpaid":
                return Response({"status": "failed"}, status=status.HTTP_200_OK)

        except stripe.error.InvalidRequestError as e:
            return Response({"status": "error", "message": str(e)})


class PaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
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

        try:
            data = request.data
            price = data["price"]
            product_name = data["product"]
            currency_code = data["currency_code"]
            callback_url = data["callback_url"]
            if price <= 0:
                return Response({"message": "price cant be zero or less than zero"})

            # check if the currency is supported by papal
            encoded_auth = base64.b64encode((f"{client_id}:{client_secret}").encode())
            url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {encoded_auth.decode()}",
                "Prefer": "return=representation",
            }
            try:
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

                response = requests.post(
                    url, headers=headers, data=json.dumps(body)
                ).json()

                print(response)
                transaction_info = TransactionDetail.objects.create(
                    payment_id=response["id"], desc=product_name
                )
                approve_payment = response["links"][1]["href"]
                return Response(
                    {"approval_url": approve_payment, "payment_id": response["id"]}
                )
            except:
                exchange_rate_obj = ExchangeRate.objects.filter(
                    currency_code__iexact=currency_code
                )

                try:
                    usd_rate = exchange_rate_obj[0].usd_exchange_rate
                except:
                    return Response(
                        {"message": f" {currency_code}, not a valid currency code."}
                    )

                converted_price = price / usd_rate

                body = {
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "amount": {
                                "currency_code": "USD",
                                "value": f"{round(converted_price,2)}",
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

                response = requests.post(
                    url, headers=headers, data=json.dumps(body)
                ).json()

                print(response)
                transaction_info = TransactionDetail.objects.create(
                    payment_id=response["id"], desc=product_name
                )
                approve_payment = response["links"][1]["href"]
                return Response(
                    {"approval_url": approve_payment, "payment_id": response["id"]}
                )
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyPaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
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

        try:
            data = request.data
            payment_id = data["id"]

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
                payment_status = response["status"]
                if payment_status == "APPROVED":
                    transaction = get_object_or_404(
                        TransactionDetail, payment_id=payment_id
                    )
                    payment_id = response["id"]
                    amount = response["purchase_units"][0]["amount"]["value"]
                    currency = response["purchase_units"][0]["amount"][
                        "currency_code"
                    ].upper()
                    name = response["purchase_units"][0]["shipping"]["name"][
                        "full_name"
                    ]
                    email = response["payer"]["email_address"]
                    city = response["purchase_units"][0]["shipping"]["address"][
                        "admin_area_2"
                    ]
                    state = response["purchase_units"][0]["shipping"]["address"][
                        "admin_area_1"
                    ]
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
                    desc = "Order details"

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
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# Generate Payment Link


@csrf_exempt
def stripe_webhook(request):
    # Retrieve the event data from the request body
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    endpoint_secret = os.getenv(
        "STRIPE_ENDPOINT_SECRETE_KEY", None
    )  # Replace with your own endpoint secret

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event based on its type
    if event["type"] == "payment_intent.succeeded":
        # Process the successful payment event
        # payment_intent = event['data']['object']
        payment_info = event["data"]["object"]["charges"]["data"][0]
        amount = (payment_info["amount"]) / 100
        currency = payment_info["currency"].upper()
        name = payment_info["billing_details"]["name"]
        email = payment_info["billing_details"]["email"]
        desc = payment_info["metadata"]["description"]
        date = payment_info["metadata"]["date"]
        city = payment_info["billing_details"]["address"]["city"]
        state = payment_info["billing_details"]["address"]["state"]
        address = payment_info["billing_details"]["address"]["line1"]
        postal_code = payment_info["billing_details"]["address"]["postal_code"]
        country_code = payment_info["billing_details"]["address"]["country"]
        order_id = payment_info["payment_intent"]
        payment_method = "Stripe"

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

    # Return a response to Stripe to acknowledge receipt of the webhook
    return HttpResponse(status=200)


@csrf_exempt
def paypal_webhook(request):
    if request.method == "POST":
        # Verify the PayPal webhook signature (optional but recommended)

        # Retrieve the webhook event data
        event_body = json.loads(request.body)

        # Process the webhook event based on its type
        event_type = event_body["event_type"]
        print("----ALL EVENT TYPE-------------")
        print(event_type)
        if event_type == "PAYMENTS.PAYMENT.CREATED":
            # Handle payment created event
            handle_payment_created(event_body)
        else:
            # Handle other event types if needed
            pass

        # Respond with an HTTP 200 status to acknowledge receipt of the webhook
        return HttpResponse(status=200)
    else:
        # Return an HTTP 405 response for unsupported request methods
        return HttpResponse(status=405)


def handle_payment_created(event_body):
    # Retrieve necessary data from the event body
    date = event_body["create_time"].split("T")[0]
    payment_id = event_body["resource"]["id"]
    info = event_body["resource"]["payer"]
    name = info["payer_info"]["shipping_address"]["recipient_name"]
    email = info["payer_info"]["email"]
    address = info["payer_info"]["shipping_address"]["line1"]
    city = info["payer_info"]["shipping_address"]["city"]
    state = info["payer_info"]["shipping_address"]["state"]
    postal_code = info["payer_info"]["shipping_address"]["postal_code"]
    country_code = info["payer_info"]["shipping_address"]["country_code"]

    transaction_info = event_body["resource"]["transactions"][0]
    amount = transaction_info["amount"]["total"]
    currency = transaction_info["amount"]["currency"]
    order_id = info["payer_info"]["payer_id"]
    desc = transaction_info["description"]
    payment_method = "Paypal"

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


# PAYMENT API FOR DOWELL INTERNAL TEAM
# Generate Payment Link


# Testing mail endpoint.
@csrf_exempt
def sending(request):
    amount = 500
    currency = "NGN"
    name = "John Doe"
    email = "sodiqb86@gmail.com"
    desc = "Book"
    date = "22-06-2022"
    city = "Alaska"
    address = "Anchorage"
    postal_code = "99501"
    order_id = "1234"
    payment_method = "stripe"

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
    return HttpResponse(res)


# class PaypalPayment(APIView):
#     @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"})


#     def post(self, request,api_key):
#         validate = processApikey(api_key)
#         try:
#             if validate["success"] == False:
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


#             elif validate["message"] == "Limit exceeded":
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)

#             elif validate["message"] == "API key is inactive":
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

#         try:
#             data = request.data
#             price = data['price']
#             product_name = data['product']
#             currency_code = data['currency_code']
#             callback_url = data['callback_url']
#             if price <= 0:
#                 return Response({'message':"price cant be zero or less than zero"})

#             # check if the currency is supported by papal
#             payment = paypalrestsdk.Payment({
#                 'intent': 'sale',
#                 'payer': {
#                     'payment_method': 'paypal'
#                 },
#                 'transactions': [{
#                     'amount': {
#                         'total':f"{price}" ,
#                         'currency': f'{currency_code.upper()}'
#                     },
#                     'description': f"{product_name}"
#                 }],
#                 'redirect_urls': {
#                     'return_url': f'{callback_url}',
#                     'cancel_url': f'{callback_url}'
#                 }
#             })


#             # Create the payment
#             if payment.create():
#                 approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
#                 payment_id = payment.id
#                 transaction_info = TransactionDetail.objects.create(payment_id=payment_id)
#                 return Response({'approval_url': approval_url,"payment_id":payment_id},status = status.HTTP_200_OK)
#             else:
#                 #If the currency is not supported by paypal, convert it to usd before processing.
#                 exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

#                 try:
#                     usd_rate = exchange_rate_obj[0].usd_exchange_rate
#                 except:
#                     return Response({"message":f" {currency_code}, not a valid currency code."})

#                 converted_price = price/usd_rate


#                 payment = paypalrestsdk.Payment({
#                     'intent': 'sale',
#                     'payer': {
#                         'payment_method': 'paypal'
#                     },
#                     'transactions': [{
#                         'amount': {
#                             'total':f"{round(converted_price,2)}" ,
#                             'currency': 'USD'
#                         },
#                         'description': f"{product_name}"
#                     }],
#                     'redirect_urls': {
#                         'return_url': f'{callback_url}',
#                         'cancel_url': f'{callback_url}'
#                     }
#                 })
#                 # Create the payment
#                 if payment.create():
#                     approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
#                     payment_id = payment.id
#                     transaction_info = TransactionDetail.objects.create(payment_id=payment_id)
#                     return Response({'approval_url': approval_url,"payment_id":payment_id},status = status.HTTP_200_OK)
#                 else:
#                     return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)


# class VerifyPaypalPayment(APIView):
#     stripe.api_key = stripe_key
#     @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})


#     def post(self, request,api_key):
#         validate = processApikey(api_key)
#         try:
#             if validate["success"] == False:
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


#             elif validate["message"] == "Limit exceeded":
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)

#             elif validate["message"] == "API key is inactive":
#                 return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

#         try:
#             data = request.data
#             payment_id = data['id']

#             try:
#                 payment_status = TransactionDetail.objects.get(payment_id=payment_id)
#                 if payment_status.status == 'succeeded':
#                     serializer = TransactionSerialiazer(payment_status)
#                     return Response({"status":"succeeded","data":serializer.data},status = status.HTTP_200_OK)

#                 else:
#                     return Response({"status":"failed"},status = status.HTTP_200_OK)
#             except stripe.error.StripeError as e:
#                 error_message = str(e)
#                 return Response({'error':error_message},status = status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
