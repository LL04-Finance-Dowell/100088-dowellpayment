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
from .models import (
    ExchangeRate,
    TransactionDetail,
    PubicTransactionDetail,
    PaymentLinkTransaction,
)
from .serializers import (
    PaymentSerializer,
    VerifyPaymentSerializer,
    PublicPaypalPaymentSerializer,
    PublicStripePaymentSerializer,
    TransactionSerialiazer,
)
from .stripe_helper import stripe_payment, verify_stripe
from .paypal_helper import paypal_payment, verify_paypal

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
from square.client import Client

load_dotenv()


class Success(View):
    template_name = "payment/success.html"

    def get(self, request):
        return render(request, self.template_name)


class Error(View):
    template_name = "payment/error.html"

    def get(self, request):
        return render(request, self.template_name)


# PAYMENT API FOR DOWELL INTERNAL TEAM


class StripePayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request):
        try:
            data = request.data
            price = data["price"]
            product = data["product"]
            currency_code = data["currency_code"]
            try:
                callback_url = data["callback_url"]
                print(callback_url)
            except:
                callback_url = "https://100088.pythonanywhere.com/api/success"
                print(callback_url)

            model_instance = TransactionDetail
            stripe_key = os.getenv("STRIPE_KEY", None)

            res = stripe_payment(
                price, product, currency_code, callback_url, stripe_key, model_instance
            )
            return res
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyStripePayment(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request):
        try:
            data = request.data
            payment_id = data["id"]
            model_instance = TransactionDetail
            stripe_key = os.getenv("STRIPE_KEY", None)

            res = verify_stripe(stripe_key, payment_id, model_instance)
            return res

        except Exception as e:
            return Response(
                {"message": "something went wrond", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # except Http404:
        #     return JsonResponse(
        #         {"status": "error", "message": "Transaction not found"}, status=404
        #     )


class PaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request):
        try:
            data = request.data
            price = data["price"]
            product_name = data["product"]
            currency_code = data["currency_code"]
            try:
                callback_url = data["callback_url"]
                print(callback_url)
            except:
                callback_url = "https://100088.pythonanywhere.com/api/success"
                print(callback_url)

            model_instance = TransactionDetail
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)

            res = paypal_payment(
                price,
                product_name,
                currency_code,
                callback_url,
                client_id,
                client_secret,
                model_instance,
            )
            return res

        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyPaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request):
        try:
            data = request.data
            payment_id = data["id"]

            model_instance = TransactionDetail
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)
            res = verify_paypal(client_id, client_secret, payment_id, model_instance)
            return res
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# PAYMENT API FOR PUBLIC USAGE


class StripePaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=PublicStripePaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data
            stripe_key = data["stripe_key"]
            price = data["price"]
            product = data["product"]
            currency_code = data["currency_code"]

            try:
                callback_url = data["callback_url"]
                print(callback_url)
            except:
                callback_url = "https://100088.pythonanywhere.com/api/success"
                print(callback_url)

            model_instance = PubicTransactionDetail
            stripe_key = stripe_key

            res = stripe_payment(
                price,
                product,
                currency_code,
                callback_url,
                stripe_key,
                model_instance,
                api_key,
            )
            return res

        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyStripePaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data
            payment_id = data["id"]
            stripe_key = data["stripe_key"]

            model_instance = PubicTransactionDetail
            stripe_key = stripe_key

            res = verify_stripe(stripe_key, payment_id, model_instance, api_key)
            return res

        except Exception as e:
            return Response(
                {"message": "something went wrond", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # except Http404:
        #     return JsonResponse(
        #         {"status": "error", "message": "Transaction not found"}, status=404
        #     )


class PaypalPaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=PublicPaypalPaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data
            client_id = data["paypal_client_id"]
            client_secret = data["paypal_secret_key"]
            price = data["price"]
            product_name = data["product"]
            currency_code = data["currency_code"]
            try:
                callback_url = data["callback_url"]
                print(callback_url)
            except:
                callback_url = "https://100088.pythonanywhere.com/api/success"
                print(callback_url)

            model_instance = PubicTransactionDetail
            client_id = client_id
            client_secret = client_secret

            res = paypal_payment(
                price,
                product_name,
                currency_code,
                callback_url,
                client_id,
                client_secret,
                model_instance,
                api_key,
            )
            return res

        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyPaypalPaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "checkout url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data
            client_id = data["paypal_client_id"]
            client_secret = data["paypal_secret_key"]
            payment_id = data["id"]

            model_instance = PubicTransactionDetail
            client_id = client_id
            client_secret = client_secret
            res = verify_paypal(
                client_id, client_secret, payment_id, model_instance, api_key
            )
            return res
        except Exception as e:
            return Response(
                {"message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# access_token = 'EAAAECow-6fY4OUq7j2SPxjBLY_FEECauFeCzuKtnaIwIEZGdyZWHQLOV85axXbL'
square = Client(
    access_token="EAAAFKvcQF8KSTZytmQmA8lT3cGxWCs-MFKt7M14IZj9fda7VD4AdbSN-pQY4yTc",
    environment="production",
)


# LGP152S55DSPV
class SquarePayment(APIView):
    def post(self, request):
        # Replace 'YOUR_SQUARE_ACCESS_TOKEN' with your actual Square Access Token

        # Create a new checkout URL
        # checkout_url = None
        # try:
        # print(access_token)
        idempotency_key = str(uuid.uuid4())

        checkout_response = square.checkout.create_payment_link(
            body={
                "redirect_url": "https://www.google.com/",  # Replace with your redirect URL
                "idempotency_key": f"{idempotency_key}",
                "description": "sample",
                "order": {
                    "location_id": "LGP152S55DSPV",
                    "line_items": [
                        {
                            "name": "Product Name",
                            "quantity": "1",
                            "base_price_money": {
                                "amount": 10000,  # Replace with the product price in cents
                                "currency": "NGN",
                            },
                        }
                    ],
                },
                "accepted_payment_methods": {"apple_pay": True, "google_pay": True},
            }
        )

        print(checkout_response.body)
        checkout_url = checkout_response.body["payment_link"]["url"]
        print(checkout_url)

        return JsonResponse({"checkout_url": checkout_url})
        # except Exception as e:
        #     return JsonResponse({'message': "something went wrong","error":f"{e}"})

    # def post(self,request):

    #     url = f"https://connect.squareup.com/v2/online-checkout/payment-links"
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Environment":"production",
    #         "Authorization": f"Bearer EAAAFKvcQF8KSTZytmQmA8lT3cGxWCs-MFKt7M14IZj9fda7VD4AdbSN-pQY4yTc",
    #     }

    #     body = {
    #         "idempotency_key": f"{str(uuid.uuid4())}",
    #         "description": "sample",
    #         "redirect_url": "https://www.google.com/",
    #         "order": {
    #         "location_id": "LGP152S55DSPV",
    #         "line_items": [
    #             {
    #             "name": "SAMPLE",
    #             "quantity": "1",
    #             "note": "SAMPLE NOTE",
    #             "base_price_money": {
    #                 "amount": 200,
    #                 "currency": "NGN"
    #             }
    #             }
    #         ]
    #         },
    #         "checkout_options": {
    #         "ask_for_shipping_address": True
    #         }
    #     }
    #     response = requests.post(url, headers=headers,data=json.dumps(body)).json()
    #     print(response)
    #     checkout_url = response["payment_link"]["url"]
    #     return Response({"message":checkout_url})


# class GenerateStripePaymentLink(APIView):
#     def post(self, request, api_key):
#         validate = processApikey(api_key)
#         print(validate)
#         try:
#             if validate["success"] == False:
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )

#             elif validate["message"] == "Limit exceeded":
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )

#             elif validate["message"] == "API key is inactive":
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )
#         except:
#             return Response(
#                 {"message": f"api_service_id: {validate['api_service_id']}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             today = date.today()
#             data = request.data
#             stripe_key = data["stripe_key"]
#             price = data["price"]
#             product_name = data["product"]
#             currency_code = data["currency_code"]
#             callback_url = data["callback_url"]
#             stripe.api_key = stripe_key
#             exchange_rate_obj = ExchangeRate.objects.filter(
#                 currency_code__iexact=currency_code
#             )

#             try:
#                 usd_rate = exchange_rate_obj[0].usd_exchange_rate
#             except:
#                 return Response(
#                     {"message": f" {currency_code}, not a valid currency code."}
#                 )

#             converted_price = price / usd_rate
#             if int(price) < 1:
#                 return Response(
#                     {
#                         "message": f"The price cannot be {price}, the lowest number acceptable is 1."
#                     }
#                 )

#             if converted_price < 0.5:
#                 return Response(
#                     {
#                         "message": f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"
#                     }
#                 )

#             try:
#                 product = stripe.Product.create(name=f"{product_name}")
#                 product_price = stripe.Price.create(
#                     unit_amount=int(price) * 100,
#                     currency=f"{currency_code.lower()}",
#                     product=f"{product.id}",
#                 )

#                 payment_link = stripe.PaymentLink.create(
#                     line_items=[{"price": f"{product_price.id}", "quantity": 1}],
#                     billing_address_collection="required",
#                     after_completion={
#                         "type": "redirect",
#                         "redirect": {
#                             "url": f"{callback_url}"
#                             + "?session_id={CHECKOUT_SESSION_ID}"
#                         },
#                     },
#                 )

#                 print(payment_link)
#                 return Response(
#                     {"payment_link": payment_link.url}, status=status.HTTP_200_OK
#                 )
#             except:
#                 product = stripe.Product.create(name=f"{product_name}")
#                 product_price = stripe.Price.create(
#                     unit_amount=int(converted_price) * 100,
#                     currency="usd",
#                     product=f"{product.id}",
#                 )

#                 payment_link = stripe.PaymentLink.create(
#                     line_items=[{"price": f"{product_price.id}", "quantity": 1}],
#                     billing_address_collection="required",
#                     after_completion={
#                         "type": "redirect",
#                         "redirect": {
#                             "url": f"{callback_url}"
#                             + "?session_id={CHECKOUT_SESSION_ID}"
#                         },
#                     },
#                 )

#                 print(payment_link)
#                 return Response(
#                     {"payment_link": payment_link.url}, status=status.HTTP_200_OK
#                 )
#         except Exception as e:
#             return Response(
#                 {"message": "something went wrong", "error": f"{e}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


# class VerifyStripePaymentLink(APIView):
#     def post(self, request, api_key):
#         validate = processApikey(api_key)
#         print(validate)
#         try:
#             if validate["success"] == False:
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )

#             elif validate["message"] == "Limit exceeded":
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )

#             elif validate["message"] == "API key is inactive":
#                 return Response(
#                     {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
#                 )
#         except:
#             return Response(
#                 {"message": f"api_service_id: {validate['api_service_id']}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             today = date.today()
#             data = request.data
#             session_id = data["id"]
#             payment_session = stripe.checkout.Session.retrieve(session_id)
#             payment_status = payment_session["payment_status"]
#             print(payment_session)

#             # Verify payment link status
#             if payment_status == "paid":
#                 check_payment_link = PaymentLinkTransaction.objects.filter(
#                     session_id=session_id
#                 )
#                 if check_payment_link:
#                     serializer = TransactionSerialiazer(check_payment_link[0])
#                     return Response(
#                         {"status": "succeeded", "data": serializer.data},
#                         status=status.HTTP_200_OK,
#                     )

#                 payment_id = payment_session["payment_intent"]
#                 amount = payment_session["amount_total"] / 100
#                 currency = payment_session["currency"].upper()
#                 name = payment_session["customer_details"]["name"]
#                 email = payment_session["customer_details"]["email"]
#                 city = payment_session["customer_details"]["address"]["city"]
#                 state = payment_session["customer_details"]["address"]["state"]
#                 address = payment_session["customer_details"]["address"]["line1"]
#                 postal_code = payment_session["customer_details"]["address"][
#                     "postal_code"
#                 ]
#                 country_code = payment_session["customer_details"]["address"]["country"]
#                 order_id = payment_id
#                 payment_method = "Stripe"
#                 desc = "Order details"

#                 res = send_mail(
#                     amount,
#                     currency,
#                     name,
#                     email,
#                     desc,
#                     today,
#                     city,
#                     address,
#                     postal_code,
#                     order_id,
#                     payment_method,
#                 )

#                 payment_link = PaymentLinkTransaction.objects.create(
#                     payment_id=payment_id,
#                     session_id=session_id,
#                     amount=amount,
#                     currency=currency,
#                     name=name,
#                     email=email,
#                     desc=desc,
#                     date=today,
#                     city=city,
#                     state=state,
#                     address=address,
#                     postal_code=postal_code,
#                     mail_sent=True,
#                     country_code=country_code,
#                     order_id=payment_id,
#                     status="succeeded",
#                 )

#                 serializer = TransactionSerialiazer(payment_link)

#                 # Payment link has been paid
#                 return Response(
#                     {"status": "succeeded", "data": serializer.data},
#                     status=status.HTTP_200_OK,
#                 )
#             elif payment_status == "unpaid":
#                 return Response({"status": "failed"}, status=status.HTTP_200_OK)

#         except stripe.error.InvalidRequestError as e:
#             return Response({"status": "error", "message": str(e)})


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
