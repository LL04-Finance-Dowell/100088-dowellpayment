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
