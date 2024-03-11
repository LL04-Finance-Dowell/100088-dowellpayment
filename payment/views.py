from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views import View
from django.conf import settings
from rest_framework.views import APIView

# from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .utils.convert_currency import convert_currency
import requests
import braintree
import stripe
from datetime import date

from .utils.sendmail import send_mail_one


from .utils.dowellconnection import (
    CreateDowellTransaction,
    UpdateDowellTransaction,
    GetDowellTransaction,
    CreateWorkflowPublicTransaction,
    UpdateWorkflowPublicTransaction,
    GetWorkflowPublicTransaction,
    CreatePublicTransaction,
    UpdatePublicTransaction,
    GetPublicTransaction,
)
from .serializers import (
    PaymentSerializer,
    VerifyPaymentSerializer,
    WorkflowStripeSerializer,
    WorkflowVerifyStripSerializer,
    WorkflowPaypalSerializer,
    WorkflowVerifyPaypalSerializer,
    PublicStripeSerializer,
    VerifyPublicStripSerializer,
    PublicPaypalSerializer,
    VerifyPublicPaypalSerializer,
)
from .utils.stripe_helper import stripe_payment, verify_stripe
from .utils.paypal_helper import paypal_payment, verify_paypal
from .utils.voucher import generate_voucher
import os
from dotenv import load_dotenv

load_dotenv()


# import plaid
# from plaid.api import plaid_api
# from plaid.model.link_token_create_request import LinkTokenCreateRequest
# from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
# from plaid.model.products import Products
# from plaid.model.country_code import CountryCode

import uuid


from .models import YapilyPaymentId


# from plaid import ApiClient

"""GET PAYPAL MODE DOWELL INTERNAL TEAM"""
dowell_paypal_mode = os.getenv("DOWELL_PAYPAL_LIVE_MODE")
if dowell_paypal_mode == "True":
    dowell_paypal_url = "https://api-m.paypal.com"
else:
    dowell_paypal_url = "https://api-m.sandbox.paypal.com"

"""GET PAYPAL MODE FOR WORKFLOW AI TEAM"""
workflow_paypal_mode = os.getenv("WORKFLOW_AI_PAYPAL_LIVE_MODE")
if workflow_paypal_mode == "True":
    workflow_paypal_url = "https://api-m.paypal.com"
else:
    workflow_paypal_url = "https://api-m.sandbox.paypal.com"

user = os.getenv("USERID")
password = os.getenv("PASSWORD")


# Show Success Page
class Success(View):
    template_name = "payment/success.html"

    def get(self, request):
        return render(request, self.template_name)


# Show error page
class Error(View):
    template_name = "payment/error.html"

    def get(self, request):
        return render(request, self.template_name)


# PAYMENT API FOR DOWELL INTERNAL TEAM

"""INITIALIZE STRIPE ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# Stripe Payment classs
class StripePayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                price = validate_data["price"]
                product = validate_data["product"]
                currency_code = validate_data["currency_code"]
                timezone = validate_data["timezone"]
                description = validate_data["description"]
                try:
                    credit = data["credit"]
                except:
                    credit = None
                callback_url = validate_data["callback_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            voucher_code = None
            if timezone and description and credit:
                try:
                    """GENERATE VOUCHER"""
                    voucher_response = generate_voucher(timezone, description, credit)
                    voucher_code = voucher_response["voucher code"]
                except:
                    return Response(
                        {
                            "success": False,
                            "message": "something went wrong",
                            "error": f"Provide correct value for timezone, description and credit",
                        },
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )
            model_instance = CreateDowellTransaction
            stripe_key = os.getenv("STRIPE_KEY", None)

            res = stripe_payment(
                price=price,
                product=product,
                currency_code=currency_code,
                callback_url=callback_url,
                stripe_key=stripe_key,
                model_instance=model_instance,
                voucher_code=voucher_code,
                generate_qrcode=True,
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR STRIPE ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# Stripe verify Payment classs
class VerifyStripePayment(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyPaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdateDowellTransaction
            model_instance_get = GetDowellTransaction
            stripe_key = os.getenv("STRIPE_KEY", None)

            res = verify_stripe(
                stripe_key=stripe_key,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# Paypal Payment classs
class PaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=PaymentSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                price = validate_data["price"]
                product_name = validate_data["product"]
                currency_code = validate_data["currency_code"]
                timezone = validate_data["timezone"]
                description = validate_data["description"]
                try:
                    credit = data["credit"]
                except:
                    credit = None
                callback_url = validate_data["callback_url"]
                print(validate_data)
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            voucher_code = None
            if timezone and description and credit:
                try:
                    """GENERATE VOUCHER"""
                    voucher_response = generate_voucher(timezone, description, credit)
                    voucher_code = voucher_response["voucher code"]
                except:
                    return Response(
                        {
                            "success": False,
                            "message": "something went wrong",
                            "error": f"Provide correct value for timezone, description and credit",
                        },
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    )

            model_instance = CreateDowellTransaction
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)

            res = paypal_payment(
                price=price,
                product_name=product_name,
                currency_code=currency_code,
                callback_url=callback_url,
                client_id=client_id,
                client_secret=client_secret,
                model_instance=model_instance,
                paypal_url=dowell_paypal_url,
                voucher_code=voucher_code,
                generate_qrcode=True,
            )
            print(res.data)
            success = res.data.get("success", False)
            print(success)
            if not success:
                print("false")
                # Call the convert_currency function here
                converted_amount = convert_currency(price, currency_code)
                print("this is converted amount")
                print(converted_amount)
                res = paypal_payment(
                    price=converted_amount,
                    product_name=product_name,
                    currency_code="usd",
                    callback_url=callback_url,
                    client_id=client_id,
                    client_secret=client_secret,
                    model_instance=model_instance,
                    paypal_url=dowell_paypal_url,
                    voucher_code=voucher_code,
                    generate_qrcode=True,
                )
                return res
            else:
                return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR PAYPAL ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# paypal verify Payment classs
class VerifyPaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=VerifyPaymentSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyPaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdateDowellTransaction
            model_instance_get = GetDowellTransaction
            client_id = os.getenv("PAYPAL_CLIENT_ID", None)
            client_secret = os.getenv("PAYPAL_SECRET_KEY", None)
            res = verify_paypal(
                client_id=client_id,
                client_secret=client_secret,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
                paypal_url=dowell_paypal_url,
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# PAYMENT API FOR WORKLOW AI INTERNAL TEAM
"""INITIALIZE STRIPE ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# stripe payment for workflow
class WorkflowStripePayment(APIView):
    @swagger_auto_schema(
        request_body=WorkflowStripeSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = WorkflowStripeSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                stripe_key = validate_data["stripe_key"]
                template_id = validate_data["template_id"]
                price = validate_data["price"]
                product = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreateWorkflowPublicTransaction
            stripe_key = stripe_key

            res = stripe_payment(
                price=price,
                product=product,
                currency_code=currency_code,
                callback_url=callback_url,
                stripe_key=stripe_key,
                model_instance=model_instance,
                template_id=template_id,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR STRIPE ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# verify stripe payment for workflow AI TEAM
class WorkflowVerifyStripePayment(APIView):
    @swagger_auto_schema(
        request_body=WorkflowVerifyStripSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = WorkflowVerifyStripSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                stripe_key = validate_data["stripe_key"]
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdateWorkflowPublicTransaction
            model_instance_get = GetWorkflowPublicTransaction
            stripe_key = stripe_key

            res = verify_stripe(
                stripe_key=stripe_key,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# paypal payment for workflow
class WorkflowPaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=WorkflowPaypalSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = WorkflowPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                template_id = validate_data["template_id"]
                price = validate_data["price"]
                product_name = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreateWorkflowPublicTransaction
            client_id = client_id
            client_secret = client_secret

            res = paypal_payment(
                price=price,
                product_name=product_name,
                currency_code=currency_code,
                callback_url=callback_url,
                client_id=client_id,
                client_secret=client_secret,
                model_instance=model_instance,
                paypal_url=workflow_paypal_url,
                template_id=template_id,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR PAYPAL ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# verify paypal payment for workflow AI team
class WorkflowVerifyPaypalPayment(APIView):
    @swagger_auto_schema(
        request_body=WorkflowVerifyPaypalSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = WorkflowVerifyPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdateWorkflowPublicTransaction
            model_instance_get = GetWorkflowPublicTransaction
            client_id = client_id
            client_secret = client_secret
            res = verify_paypal(
                client_id=client_id,
                client_secret=client_secret,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
                paypal_url=workflow_paypal_url,
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# PAYMENT API FOR PUBLIC USAGE
"""INITIALIZE STRIPE ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# Stripe Payment for Public User
class StripePaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=PublicStripeSerializer, responses={200: "approval_url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data
            serializer = PublicStripeSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                stripe_key = validate_data["stripe_key"]
                price = validate_data["price"]
                product = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreatePublicTransaction
            stripe_key = stripe_key

            res = stripe_payment(
                price=price,
                product=product,
                currency_code=currency_code,
                callback_url=callback_url,
                stripe_key=stripe_key,
                model_instance=model_instance,
                api_key=api_key,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR STRIPE ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# verify Stripe Payment for Public User
class VerifyStripePaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=VerifyPublicStripSerializer, responses={200: "status"}
    )
    def post(self, request, api_key):
        try:
            data = request.data

            serializer = VerifyPublicStripSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                stripe_key = validate_data["stripe_key"]
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdatePublicTransaction
            model_instance_get = GetPublicTransaction
            stripe_key = stripe_key

            res = verify_stripe(
                stripe_key=stripe_key,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
                api_key=api_key,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# paypal Payment for Public User
class PaypalPaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=PublicPaypalSerializer, responses={200: "approval_url"}
    )
    def post(self, request, api_key):
        try:
            data = request.data

            serializer = PublicPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                price = validate_data["price"]
                product_name = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
                public_paypal_url = validate_data["public_paypal_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreatePublicTransaction
            client_id = client_id
            client_secret = client_secret

            res = paypal_payment(
                price=price,
                product_name=product_name,
                currency_code=currency_code,
                callback_url=callback_url,
                client_id=client_id,
                client_secret=client_secret,
                model_instance=model_instance,
                paypal_url=public_paypal_url,
                api_key=api_key,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR PAYPAL ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


# verify paypal Payment for Public User
class VerifyPaypalPaymentPublic(APIView):
    @swagger_auto_schema(
        request_body=VerifyPublicPaypalSerializer, responses={200: "status"}
    )
    def post(self, request, api_key):
        try:
            data = request.data

            serializer = VerifyPublicPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                payment_id = validate_data["id"]
                public_paypal_url = validate_data["public_paypal_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdatePublicTransaction
            model_instance_get = GetPublicTransaction
            client_id = client_id
            client_secret = client_secret
            res = verify_paypal(
                client_id=client_id,
                client_secret=client_secret,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
                paypal_url=public_paypal_url,
                api_key=api_key,
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


# PAYMENT API FOR PUBLIC USAGE WITHOUT API KEYS
"""INITIALIZE STRIPE ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


# stripe Payment for Public User without API KEYs
class StripePaymentPublicUse(APIView):
    @swagger_auto_schema(
        request_body=PublicStripeSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data
            serializer = PublicStripeSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                stripe_key = validate_data["stripe_key"]
                price = validate_data["price"]
                product = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreatePublicTransaction
            stripe_key = stripe_key

            res = stripe_payment(
                price=price,
                product=product,
                currency_code=currency_code,
                callback_url=callback_url,
                stripe_key=stripe_key,
                model_instance=model_instance,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR STRIPE ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


class VerifyStripePaymentPublicUse(APIView):
    @swagger_auto_schema(
        request_body=VerifyPublicStripSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = VerifyPublicStripSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                stripe_key = validate_data["stripe_key"]
                payment_id = validate_data["id"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdatePublicTransaction
            model_instance_get = GetPublicTransaction
            stripe_key = stripe_key

            res = verify_stripe(
                stripe_key=stripe_key,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


class PaypalPaymentPublicUse(APIView):
    @swagger_auto_schema(
        request_body=PublicPaypalSerializer, responses={200: "approval_url"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = PublicPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                price = validate_data["price"]
                product_name = validate_data["product"]
                currency_code = validate_data["currency_code"]
                callback_url = validate_data["callback_url"]
                public_paypal_url = validate_data["public_paypal_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance = CreatePublicTransaction
            client_id = client_id
            client_secret = client_secret

            res = paypal_payment(
                price=price,
                product_name=product_name,
                currency_code=currency_code,
                callback_url=callback_url,
                client_id=client_id,
                client_secret=client_secret,
                model_instance=model_instance,
                paypal_url=public_paypal_url,
                generate_qrcode=True,
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR PAYPAL ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


class VerifyPaypalPaymentPublicUse(APIView):
    @swagger_auto_schema(
        request_body=VerifyPublicPaypalSerializer, responses={200: "status"}
    )
    def post(self, request):
        try:
            data = request.data

            serializer = VerifyPublicPaypalSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                client_id = validate_data["paypal_client_id"]
                client_secret = validate_data["paypal_secret_key"]
                payment_id = validate_data["id"]
                public_paypal_url = validate_data["public_paypal_url"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            model_instance_update = UpdatePublicTransaction
            model_instance_get = GetPublicTransaction
            client_id = client_id
            client_secret = client_secret
            res = verify_paypal(
                client_id=client_id,
                client_secret=client_secret,
                payment_id=payment_id,
                model_instance_update=model_instance_update,
                model_instance_get=model_instance_get,
                paypal_url=public_paypal_url,
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


def serve_pdf(request, pdf_filename):
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
            return response
    else:
        return HttpResponse("PDF not found", status=404)


class TinkCreatePayment(APIView):
    def post(self, request):
        url = "https://api.tink.com/api/v1/oauth/token"

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_id": f"{os.getenv('CLIENT_ID')}",
            "client_secret": f"{os.getenv('CLIENT_SECRET')}",
            "grant_type": "client_credentials",
            "scope": "payment:read,payment:write",
        }

        res = requests.post(url, data=data, headers=headers).json()

        access_token = res["access_token"]
        print("access_token", access_token)

        url2 = "https://api.tink.com/api/v1/payments/requests"
        headers2 = {
            "Content-Type": "application/json;charset=UTF-8",
            "Authorization": f"Bearer {access_token}",
        }
        data2 = {
            "destinations": [
                {"accountNumber": "IT60X0542811101000000123456", "type": "iban"}
            ],
            "amount": 10,
            "currency": "SEK",
            "market": "SE",
            "recipientName": "Test AB",
            "sourceMessage": "Payment for Gym Equipment",
            "remittanceInformation": {
                "type": "UNSTRUCTURED",
                "value": "CREDITOR REFERENCE",
            },
            "paymentScheme": "SEPA_CREDIT_TRANSFER",
        }

        res2 = requests.post(url2, json=data2, headers=headers2).json()
        id = res2["id"]
        print(id)
        auth = f"https://link.tink.com/1.0/pay/?client_id={os.getenv('CLIENT_ID')}&redirect_uri=https://www.google.com/&market=SE&locale=en_US&payment_request_id={id}"
        print(auth)
        return Response(auth)


class ProcessGooglePaymentView(APIView):
    def post(self, request, *args, **kwargs):
        payment_method_nonce = request.data.get("payment_method_nonce")
        amount = request.data.get("price")
        product = request.data.get("product")
        currency_code = request.data.get("currency_code")
        timezone = request.data.get("timezone")
        description = request.data.get("description")

        result = self.process_payment(amount,payment_method_nonce)
        if result.is_success:
            return Response(
                {
                    "success":True,
                    "message":"Payment successful"
                }
            )
        else:
            return Response(
                {
                    "success":False,
                    "message":"Payment failed"
                }
            )
    def process_payment(self, amount, payment_method_nonce):
        # Configure Braintree
        braintree.Configuration.configure(braintree.Environment.Sandbox,
                                          merchant_id='kdjtyhnjd3htx2hw',
                                          public_key='mv54hqv65snshzjv',
                                          private_key='369e38d36edc938b0346a35ecd4150aa')

        # Process payment using Braintree
        result = braintree.Transaction.sale({
            'amount': str(amount),
            'payment_method_nonce': payment_method_nonce,
            'options': {
                'submit_for_settlement': True
            }
        })
        print(result)
        return result

class BraintreeClientTokenView(APIView):
    def get(self, request, *args, **kwargs):
        # Replace 'your_braintree_merchant_id', 'your_braintree_public_key', and 'your_braintree_private_key' with your actual Braintree credentials
        braintree.Configuration.configure(braintree.Environment.Sandbox,
                                          merchant_id='kdjtyhnjd3htx2hw',
                                          public_key='mv54hqv65snshzjv',
                                          private_key='369e38d36edc938b0346a35ecd4150aa')

        client_token = braintree.ClientToken.generate()

        return Response({'clientToken': client_token})


class ManualEmail(APIView):
    def post(self,request):
        # Extract data from request.data
        amount = request.data.get('amount')
        currency = request.data.get('currency')
        name = request.data.get('name')
        email = request.data.get('email')
        desc = request.data.get('desc')
        date = request.data.get('date')
        city = request.data.get('city')
        address = request.data.get('address')
        postal_code = request.data.get('postal_code')
        ref_id = request.data.get('ref_id')
        invoice_number = request.data.get('invoice_number')
        order_number = request.data.get('order_number')
        payment_method = request.data.get('payment_method')
        territory = request.data.get('territory')

        # Call send_mail_function
        success = send_mail_one(
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
            territory,
        )
        print(success)
        if success:
            return Response({"success": True, "message": "Email sent successfully"})
        else:
            return Response({"success": False, "message": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




"""

STRIPE PAYMENT FOR Q

"""

class StripeQPayment(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = PaymentSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.to_representation(serializer.validated_data)
                amount = validate_data["price"]
                product = validate_data["product"]
                currency_code = validate_data["currency_code"]
            else:
                errors = serializer.errors
                return Response(
                    {"success": False, "errors": errors},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            today = date.today()
            unique_id = uuid.uuid4()
            payment_id = str(unique_id)

            stripe_key = os.getenv("STRIPE_KEY", None)
            stripe.api_key = "sk_test_51NNYXvEifafv1oQMU0qOz9DrfLNNB5WG2jnHAzxmizAdUHU7T1Yk4EfUshB5A5fCNZBRCrB1Vk2P5N272Frgmd3E00UqN7mPbn"

            session = stripe.checkout.Session.create(
    payment_method_types=["card", "cashapp","google"],  # Use "wallet_google_pay" for Google Pay
    line_items=[
        {
            "price_data": {
                "currency": currency_code,
                "product_data": {
                    "name": "Q payment",
                },
                "unit_amount": f"{(amount) * 100}",
            },
            "quantity": 1,
        }
    ],
    mode="payment",
    success_url=f"https://100088.pythonanywhere.com/api/stripe-callback?payment_id={payment_id}",
    cancel_url=f"https://100088.pythonanywhere.com/api/stripe-callback?payment_id={payment_id}",
    billing_address_collection="required",
    payment_intent_data={
        "metadata": {
            "description": "Q payment",
            "payment_id": payment_id,
            "date": today,
        }
    },
)
            transaction = CreateDowellTransaction(

                payment_id,
                session_id = session.id,
                desc = product,
                today =today,
                template_id=None,
                voucher_code=None

            )
            print(session)
            print(transaction)
            # transaction = CreateUserTransaction(
            #     username,
            #     email,
            #     amount,
            #     payment_id,
            #     session.id,
            #     today,
            #     transaction_type="Deposit",
            #     status="Failed",
            # )
            return Response(
                {"success": True,
                  "approval_url": f"{session.url}",
                  "payment_id":payment_id},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class StripeCallback(APIView):
    def get(self, request, *args, **kwargs):
        print("---called---callback")
        try:
            # Extract payment_id from the query parameters
            payment_id = request.query_params.get('payment_id')

            # Retrieve the Stripe transaction using the payment_id
            stripe_key = os.getenv("STRIPE_KEY", None)
            stripe.api_key = stripe_key
            model_instance_update = UpdateDowellTransaction
            model_instance_get = GetDowellTransaction
            transaction = model_instance_get(payment_id)
            session_id = transaction["data"]["session_id"]
            payment_session = stripe.checkout.Session.retrieve(session_id)
            print(payment_session)
            payment_status = payment_session["payment_status"]
            state = payment_session["status"]
            print(payment_session)
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
                    country = payment_session["customer_details"]["address"]["country"]
                except:
                    country = ""
                try:
                    state = payment_session["customer_details"]["address"]["state"]
                    print("state", state)
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
            # Here you can update your database or perform any other actions based on the payment result

            return Response({
                'success': True,
                'message': 'Payment callback received successfully',
                'transaction_status': payment_status
            })

        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error processing payment callback',
                'error': str(e)
            }, status=400)




class PaytmCheckout(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Extract required parameters from request data
            amount = request.data.get('amount')
            customer_id = request.data.get('customer_id')
            mobile_number = request.data.get('mobile_number')
            email = request.data.get('email')

            # Replace these values with your Paytm credentials
            PAYTM_MERCHANT_ID = "your_merchant_id"
            PAYTM_SECRET_KEY = "your_secret_key"
            PAYTM_WEBSITE = "WEBSTAGING"  # Change it to "DEFAULT" for production environment

            # Define Paytm API endpoint
            paytm_api_url = "https://securegw-stage.paytm.in/link/create"

            # Construct request payload
            payload = {
                "body": {
                    "requestType": "Payment",
                    "mid": PAYTM_MERCHANT_ID,
                    "websiteName": PAYTM_WEBSITE,
                    "orderId": "order123",  # Replace with your unique order ID
                    "callbackUrl": "http://your_website.com/payment/response/",  # Replace with your callback URL
                    "txnAmount": {
                        "value": amount,
                        "currency": "INR",
                    },
                    "userInfo": {
                        "custId": customer_id,
                        "mobile": mobile_number,
                        "email": email,
                    }
                },
                "head": {
                    "tokenType": "AES",
                    "signature": "your_signature",
                }
            }

            # Make POST request to Paytm API
            response = requests.post(paytm_api_url, json=payload)
            response_data = response.json()

            # Extract checkout link from response
            checkout_link = response_data.get('body', {}).get('resultInfo', {}).get('checkoutUrl')

            return Response({"checkout_link": checkout_link})

        except Exception as e:
            return Response({"error": str(e)}, status=500)







# return list of supported country by yapily for the user so that the user can pick one
# query yapily to get the list of banks and cache it response from yapily
# base on the country selected return the banks that are in that country to the frontend
# extract the (bank name, bank id, bank image url and bank country)

# """
# to initialize the payment, the client side will return to me the BANK ID, AMOUNT and BANK COUNTRY
# base on the bank id i will query the cache to find out the BANK FEATURES (domestic or international)

# """


# class YapilySupportedCountry(APIView):
#     def get(self, request):
#         supported_countries = [
#             {
#                 "contry_code": "AT",
#                 "country_name": "Austria",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/1pYGpQKFjdF9thBP0KI8Lf/1bb4d414d2a882775a3560df4cdb3cb2/Austria.svg",
#             },
#             {
#                 "contry_code": "BE",
#                 "country_name": "Belgium",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/3s2yZ0OCbjEsWq7NrRqddS/3e775d276719039ac54211f0a175a492/be.svg",
#             },
#             {
#                 "contry_code": "DK",
#                 "country_name": "Denmark",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/5Z4JDgKwFarKXq48280huj/ff4b3d43035d03ab106d92a6a0fe9b6e/dk.svg",
#             },
#             {
#                 "contry_code": "EE",
#                 "country_name": "Estonia",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/Lv4EOakJXdByW69vff7UJ/5f0345fd4cc3798b5c159c3fd49563f3/ee.svg",
#             },
#             {
#                 "contry_code": "FI",
#                 "country_name": "Finland",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/22bzAFwoRiwtHSIgnBLTg/35d27ea55e76f08611e88330c2b496ca/fi.svg",
#             },
#             {
#                 "contry_code": "FR",
#                 "country_name": "France",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/659TuuXEmdyz3KMBZq5Mjl/5ece587f440a055e31ec5266fce0a033/France.svg",
#             },
#             {
#                 "contry_code": "DE",
#                 "country_name": "Germany",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/2rrNAoN0bxWraLHue78giT/0fe7fa8b1463d1b0e37780fbbabcbf59/Germany.svg",
#             },
#             {
#                 "contry_code": "IS",
#                 "country_name": "Iceland",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/22C6Klm3ezYfSelnhtUqa4/db019ea9c1fffeb97ff8fe0f5e761389/is.svg",
#             },
#             {
#                 "contry_code": "IE",
#                 "country_name": "Ireland",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/6FKGHt1Bgr7hD1f2MeQo6e/135072161a7d3b183b139e370304bd95/Ireland.svg",
#             },
#             {
#                 "contry_code": "IT",
#                 "country_name": "Italy",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/2p7zgSHmn9S1wW0ImpCMJB/0bdca83e6641a9a1633643c347bce6ed/Italy.svg",
#             },
#             {
#                 "contry_code": "LV",
#                 "country_name": "Latvia",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/1K8VSyX6RfTIYgEHm3W68v/bca75e21dfdb99abe3fade3651068f1e/lv.svg",
#             },
#             {
#                 "contry_code": "LT",
#                 "country_name": "Lithuania",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/5GOFHsXmd7wyO1dqDIH3As/860f6af5b72558452f43c4142a0ec0b2/lt.svg",
#             },
#             {
#                 "contry_code": "NL",
#                 "country_name": "Netherlands",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/6wBgYzOaA1yp9GC8USPsg8/0122f80fef8e39e8d02b6d963c0a962e/Netherlands.svg",
#             },
#             {
#                 "contry_code": "NO",
#                 "country_name": "Norway",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/1apjST7XVYfsrxByUAVZ33/8b320c0d43d869b7fc72bf380d1ff1d1/no.svg",
#             },
#             {
#                 "contry_code": "PL",
#                 "country_name": "Poland",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/5AEwDH3kLmaEuADSM10PMB/e29849065565db645a639b7002892572/pl.svg",
#             },
#             {
#                 "contry_code": "PT",
#                 "country_name": "Portugal",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/4sfNqcCfxxGaI0RR7XCY0a/6836d1aee7e23ebeb62b2db057826030/pt-flag.svg",
#             },
#             {
#                 "contry_code": "ES",
#                 "country_name": "Spain",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/3GnXQHnVJ2cu4zALoUhZfi/0eb82ee9e60787e27f443bfce248cb6f/Spain.svg",
#             },
#             {
#                 "contry_code": "SE",
#                 "country_name": "Sweden",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/6kU0kapUi0xDFQgqDsmuWu/e1db852a8052e4f79be77c2249fdd823/se.svg",
#             },
#             {
#                 "contry_code": "GB",
#                 "country_name": "United Kingdom",
#                 "country_logo": "https://images.ctfassets.net/3ndxs7efitel/44qItkbYe7KHixMQd0gDBX/235a06da9c86a344b7cdcc70f933ef42/UK.svg",
#             },
#         ]
#         return Response(
#             {
#                 "success": True,
#                 "count": len(supported_countries),
#                 "data": supported_countries,
#             }
#         )

#     def post(self, request):
#         data = request.data
#         country_code = data["country_code"]

#         headers = {"Content-Type": "application/json;charset=UTF-8"}

#         url = "https://api.yapily.com/institutions"

#         response = requests.get(url, headers=headers, auth=(user, password))

#         res_data = response.json()
#         print(res_data)
#         context = []
#         banks = res_data["data"]
#         for bank in banks:
#             supported_country_bank = bank["countries"]
#             for country in supported_country_bank:
#                 if country_code == country["countryCode2"]:
#                     bank_id = bank["id"]
#                     bank_name = bank["name"]
#                     code = country_code
#                     bank_logo = bank["media"][0]["source"]
#                     context.append(
#                         {
#                             "bank_id": bank_id,
#                             "bank_name": bank_name,
#                             "country_code": code,
#                             "bank_logo": bank_logo,
#                         }
#                     )

#         return Response(context)


# class InitializeNetPaymentYapily(APIView):
#     def post(self, request):
#         data = request.data
#         amount = data["amount"]
#         currency_code = data["currency_code"]
#         bank_id = data["bank_id"]
#         country_code = data["country_code"]
#         # email = data["email"]
#         product_desc = data["product"]

#         unique_id = uuid.uuid4()
#         paymentIdempotencyId = str(unique_id).replace("-", "")

#         headers1 = {"Content-Type": "application/json;charset=UTF-8"}

#         url1 = "https://api.yapily.com/institutions"

#         response1 = requests.get(url1, headers=headers1, auth=(user, password))
#         res_data1 = response1.json()
#         banks = res_data1["data"]
#         for bank in banks:
#             # print(bank["name"])
#             if bank_id == bank["id"]:
#                 bank_features = bank["features"]
#                 if (
#                     "CREATE_DOMESTIC_SINGLE_PAYMENT" in bank_features
#                     and country_code == "GB"
#                 ):
#                     payment_type = "DOMESTIC_PAYMENT"
#                 if (
#                     "CREATE_INTERNATIONAL_SINGLE_PAYMENT" in bank_features
#                     and country_code != "GB"
#                 ):
#                     payment_type = "INTERNATIONAL_PAYMENT"

#                 if (
#                     "CREATE_DOMESTIC_SINGLE_PAYMENT" in bank_features
#                     and "CREATE_INTERNATIONAL_SINGLE_PAYMENT" in bank_features
#                     and country_code == "GB"
#                 ):
#                     payment_type = "DOMESTIC_PAYMENT"

#         url = "https://api.yapily.com/payment-auth-requests"

#         query = {"raw": "true"}
#         "modelo-sandbox"

#         if payment_type == "DOMESTIC_PAYMENT":
#             print("DOMESTIC_PAYMENT")
#             payload = {
#                 "forwardParameters": [paymentIdempotencyId],
#                 "applicationUserId": "john.doe@company.com",
#                 "institutionId": f"{bank_id}",
#                 "callback": "http://127.0.0.1:8000/api/yapily/create/payment",
#                 "paymentRequest": {
#                     "paymentIdempotencyId": f"{paymentIdempotencyId}",
#                     "amount": {"amount": amount, "currency": f"{currency_code}"},
#                     "reference": f"{product_desc}",
#                     "type": f"{payment_type}",
#                     "payee": {
#                         "name": "Jane Doe",
#                         "address": {"country": "GB"},
#                         "accountIdentifications": [
#                             {"type": "SORT_CODE", "identification": "123456"},
#                             {"type": "ACCOUNT_NUMBER", "identification": "12345678"},
#                         ],
#                     },
#                 },
#             }
#         if payment_type == "INTERNATIONAL_PAYMENT":
#             print("INTERNATIONAL_PAYMENT")
#             payload = {
#                 "forwardParameters": [paymentIdempotencyId],
#                 "applicationUserId": "john.doe@company.com",
#                 "institutionId": f"{bank_id}",
#                 "callback": "http://127.0.0.1:8000/api/yapily/create/payment",
#                 "paymentRequest": {
#                     "paymentIdempotencyId": f"{paymentIdempotencyId}",
#                     "amount": {"amount": amount, "currency": f"{currency_code}"},
#                     "reference": f"{product_desc}",
#                     "type": f"{payment_type}",
#                     "payee": {
#                         "name": "Jane Doe",
#                         "address": {"country": "GB"},
#                         "accountIdentifications": [
#                             {"type": "BIC", "identification": "RBOSGB2109M"},
#                             {
#                                 "type": "IBAN",
#                                 "identification": "GB29RBOS83040210126939",
#                             },
#                         ],
#                     },
#                     "internationalPayment": {"currencyOfTransfer": f"{currency_code}"},
#                 },
#             }

#         headers = {
#             "Content-Type": "application/json;charset=UTF-8",
#             "psu-id": "string",
#             "psu-corporate-id": "string",
#             "psu-ip-address": "string",
#         }

#         response = requests.post(
#             url, json=payload, headers=headers, params=query, auth=(user, password)
#         )

#         res_data = response.json()
#         print("-------------------------------------")
#         print(res_data)
#         print("----------------------------------------")
#         date = res_data["data"]["createdAt"].split("T")[0]
#         # print(date)
#         obj = YapilyPaymentId.objects.create(
#             payment_idempotency_id=paymentIdempotencyId,
#             amount=amount,
#             currency_code=currency_code,
#             bank_id=bank_id,
#             desc=product_desc,
#             date=date,
#             payment_type=payment_type,
#             country_code=country_code,
#         )

#         return Response(
#             {
#                 "authorisationUrl": res_data["data"]["authorisationUrl"],
#                 "qrcode_url": res_data["data"]["qrCodeUrl"],
#                 # "data":res_data,
#             }
#         )


# class CreateNetPaymentYapily(APIView):
#     def get(self, request):
#         full_url = request.get_full_path()
#         paymentIdempotencyId = full_url.split("&")[-1][:-1]
#         consent = request.GET.get("consent")

#         obj = YapilyPaymentId.objects.get(payment_idempotency_id=paymentIdempotencyId)
#         amount = obj.amount
#         currency_code = obj.currency_code
#         product_desc = obj.desc

#         url = "https://api.yapily.com/payments"

#         headers = {
#             "Content-Type": "application/json;charset=UTF-8",
#             "consent": f"{consent}",
#             "psu-id": "string",
#             "psu-corporate-id": "string",
#             "psu-ip-address": "string",
#         }

#         query = {"raw": "true"}

#         payload = {
#             "paymentIdempotencyId": f"{paymentIdempotencyId}",
#             "amount": {"amount": amount, "currency": f"{currency_code}"},
#             "reference": f"{product_desc}",
#             "type": "DOMESTIC_PAYMENT",
#             "payee": {
#                 "name": "Jane Doe",
#                 "address": {"country": "GB"},
#                 "accountIdentifications": [
#                     {"type": "SORT_CODE", "identification": "123456"},
#                     {"type": "ACCOUNT_NUMBER", "identification": "12345678"},
#                 ],
#             },
#         }

#         response = requests.post(
#             url, json=payload, headers=headers, params=query, auth=(user, password)
#         )
#         print("----------------------------------")
#         data = response.json()
#         print(data)
#         print("----------------------------------")
#         id = data["data"]["id"]
#         debtor_name = data["raw"][0]["result"]["Data"]["Debtor"]["Name"]
#         status = data["data"]["status"]
#         obj.payment_id = id
#         obj.consent_token = consent
#         obj.payment_status = status
#         obj.name = debtor_name
#         obj.save()
#         redirect_url = f"https://www.google.com/?payment_id={id}"
#         response = HttpResponseRedirect(redirect_url)
#         return response


# class VerifyNetPaymentYapily(APIView):
#     def post(self, request):
#         data = request.data
#         payment_id = data["id"]

#         url = "https://api.yapily.com/payments/" + payment_id + "/details"

#         headers = {
#             "consent": f"{consent}",
#             "psu-id": "string",
#             "psu-corporate-id": "string",
#             "psu-ip-address": "string",
#         }

#         query = {"raw": "true"}

#         obj = YapilyPaymentId.objects.get(payment_id=payment_id)
#         consent = obj.consent_token

#         response = requests.get(
#             url, headers=headers, params=query, auth=(user, password)
#         )

#         data = response.json()
#         print("--------------------------------")
#         print(data)
#         print("---------------------------------")
#         status = data["data"]["payments"][0]["status"]
#         # debtor_name = data["raw"][0]["result"]["Data"]["Debtor"]["Name"]

#         if status == "COMPLETED":
#             print("status", status)
#         else:
#             print("status", status)
#         obj.payment_status = status

#         obj.save()
#         return Response(data)


# PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
# PLAID_SECRET = os.getenv("PLAID_SECRET")

# configuration = plaid.Configuration(
#     host=plaid.Environment.Sandbox,
#     api_key={
#         "clientId": PLAID_CLIENT_ID,
#         "secret": PLAID_SECRET,
#     },
# )
# api_client = plaid.ApiClient(configuration)
# client = plaid_api.PlaidApi(api_client)


# class NetPaymentPlaid(APIView):
#     def post(self, request):
#         request = LinkTokenCreateRequest(
#             products=[Products("auth")],
#             client_name="Plaid Test App",
#             country_codes=[CountryCode("US")],
#             redirect_uri="https://100088.pythonanywhere.com/api/success",
#             language="en",
#             webhook="https://webhook.example.com",
#             user=LinkTokenCreateRequestUser(client_user_id="user-id"),
#         )
#         response = client.link_token_create(request)
#         print(response)

#         return Response({"message": response.to_dict()})


# class GetAllBank(APIView):
#     def get(self, request):
#         url = "https://api.sandbox.token.io/v2/banks"
#         # url = "https://api.token.io/banks"

#         query = {
#             "supportsSinglePayment": "true",
#         }

#         response = requests.get(url, params=query)

#         data = response.json()
#         print(data)

#         return Response(data)

# class CreatePayment(APIView):
#     def post(self, request):
#         url = "https://api.sandbox.token.io/v2/payments"
#         # url = "https://api.token.io/payments"

#         payload = {
#             "initiation": {
#                 "bankId": "ngp-actv",
#                 "refId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq",
#                 "remittanceInformationPrimary": "RemittancePrimary",
#                 "remittanceInformationSecondary": "RemittanceSecondary",
#                 "onBehalfOfId": "c5a863bc-86f2-4418-a26f-25b24c7983c7",
#                 "amount": {"value": "10.23", "currency": "EUR"},
#                 "localInstrument": "SEPA",
#                 "debtor": {
#                     "memberId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq",
#                     "iban": "GB29NWBK60161331926819",
#                     "bic": "BOFIIE2D",
#                     "name": "John Smith",
#                     "ultimateDebtorName": "John Smith",
#                     "address": {
#                         "streetName": "221B",
#                         "buildingNumber": "2C",
#                         "postCode": "E1 6AN",
#                         "townName": "Saint Ives",
#                         "country": "United Kingdom",
#                     },
#                 },
#                 "creditor": {
#                     "memberId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq",
#                     "iban": "GB29NWBK60161331926819",
#                     "bic": "BOFIIE2D",
#                     "name": "Customer Inc.",
#                     "ultimateCreditorName": "Customer Inc.",
#                     "address": {
#                         "streetName": "221B",
#                         "buildingNumber": "2C",
#                         "postCode": "E1 6AN",
#                         "townName": "Saint Ives",
#                         "country": "United Kingdom",
#                     },
#                     "bankName": "string",
#                 },
#                 "executionDate": "2023-04-29",
#                 "confirmFunds": False,
#                 "returnRefundAccount": False,
#                 "disableFutureDatedPaymentConversion": False,
#                 "callbackUrl": "https://100088.pythonanywhere.com/api/success",
#                 "callbackState": "c070b02c-4cca-4ee1-9c1a-537c98ad162e",
#                 "chargeBearer": "CRED",
#                 "risk": {
#                     "psuId": "0000789123",
#                     "paymentContextCode": "PISP_PAYEE",
#                     "paymentPurposeCode": "DVPM",
#                     "merchantCategoryCode": "4812",
#                     "beneficiaryAccountType": "BUSINESS",
#                     "contractPresentIndicator": True,
#                     "beneficiaryPrepopulatedIndicator": True,
#                 },
#             },
#             "pispConsentAccepted": False,
#             "initialEmbeddedAuth": {"username": "John Smith"},
#         }
#         api_key = os.getenv("API_KEY")
#         print(api_key)
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Basic {api_key}",
#         }

#         response = requests.post(url, json=payload, headers=headers)

#         data = response.json()
#         print(data)

#         return Response(data)


# class CreatePayment(APIView):
#     def post(self,request):

#         #url = "https://api.sandbox.token.io/v2/payments"
#         #url = "https://api.token.io/payments"


#         url = "https://api.token.io/token-requests"

#         payload = {
#         "requestOptions": {
#             "bankId": "goldbank",
#             "from": {
#             "alias": {
#                 "realmId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq",
#                 "type": "EMAIL",
#                 "value": "e-sales@token.io"
#             },
#             "id": "m:nP4w3u5y8ddrxDJkjimgSX9e4fZ:5zKtXEAq"
#             },
#             "psuId": "a:TASDo3124fcsmF0vsmdv4mf4mklsdwls3mcixz14fkasdv5",
#             "receiptRequested": False,
#             "tokenInternal": {
#             "redirectUrl": "http://psu-redirect.com",
#             "usingWebApp": False
#             }
#         },
#         "requestPayload": {
#             "actingAs": {
#             "displayName": "The Great Baking Co.",
#             "refId": "9htio4a1sp2akdr1aa",
#             "secondaryName": "jane.doe@company.com"
#             },
#             "callbackState": "https://{callback-url}?signature=%7B%22memberId%22%3A%22m%3A3rKtsoKaE1QUti3KCWPrcSQYvJj9% 3A5zKtXEAq%22%2C%22keyId%22%3A%22lgf2Mn0G4kkcXd5m%22%2C%22signature%22%3A%22Md-2D G0X9PpuOxea0iK33cAZ2Ffk6E5I1mAcJS6YywU80Q0yYBOlwvGy37dmovmH_OC7Jl8c-fxQ5gP2RWTaDw%22%7D& state=%257B%2522csrfTokenHash%2522%253A%2522pod1e6xornyoesn2sp%2522%257D& tokenId=ta%3AHWowFawmAwiuPKNdM7xjpiQktPppgK2JatsWPZAyTHcq%3A5zKtXEAq",
#             "countries": [
#             "DE",
#             "IT",
#             "RO"
#             ],
#             "description": "A regular payment",
#             "disableFutureDatedPaymentConversion": False,
#             "redirectUrl": "http://psu-redirect.com",
#             "refId": "9htio4a1sp2akdr1aa",
#             "to": {
#             "alias": {
#                 "realmId": "m:vHZUAMFt6s64vn6aDyMiwBYbPDN:5zKtXEAq",
#                 "type": "EMAIL",
#                 "value": "e-sales@token.io"
#             },
#             "id": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq"
#             },
#             "userRefId": "3jdaWmcewrj3MX0CDS",
#             "transferBody": {
#             "confirmFunds": False,
#             "currency": "EUR",
#             "executionDate": "2023-02-28",
#             "instructions": {
#                 "metadata": {
#                 "chargeBearer": "CRED",
#                 "providerTransferMetadata": {
#                     "cma9TransferMetadata": {
#                     "endToEndIdentification": "string",
#                     "instructionIdentification": "string",
#                     "risk": {}
#                     }
#                 },
#                 "purposeCode": "CBLK",
#                 "ultimateCreditor": "ACME GmbH",
#                 "ultimateDebtor": "John Smith"
#                 },
#                 "source": {
#                 "accountIdentifier": {
#                     "bankgiro": {
#                     "bankgiroNumber": "56781234"
#                     }
#                 },
#                 "bankId": "ob-iron",
#                 "bic": "BOFIIE2D",
#                 "customerData": {
#                     "address": {
#                     "city": "Berlin",
#                     "conscriptionNumber": "2831",
#                     "country": "Germany",
#                     "district": "Friedrichshain",
#                     "flats": "21A - 21C",
#                     "full": "Fifth house on the left after the village oak, Smalltown, Smallcountry",
#                     "hamlet": "Botzowviertel",
#                     "houseName": "Grossen Blauen Haus",
#                     "houseNumber": "123",
#                     "place": "Arnswalder Platz",
#                     "postCode": "10243",
#                     "province": "BC",
#                     "state": "CA",
#                     "street": "Hans-Otto-Strasse",
#                     "subdistrict": "Friedrichshain Nord",
#                     "suburb": "Altona Meadows Suburb"
#                     },
#                     "legalNames": "Mr John Arthur Smith"
#                 }
#                 },
#                 "transferDestinations": [
#                 {
#                     "customerData": {
#                     "address": {},
#                     "legalNames": "Mr John Arthur Smith"
#                     },
#                     "type": "BUSINESS",
#                     "sepa": {
#                     "iban": "GB29NWBK60161331926819",
#                     "bic": "BOFIIE2D"
#                     }
#                 }
#                 ]
#             },
#             "lifetimeAmount": "10000.00",
#             "remittanceReference": "MFt6s64vn6aDyMiwBA3",
#             "returnRefundAccount": False,
#             "setTransferDestinationsUrl": "string"
#             }
#         }
#         }
#         api_key = os.getenv("API_KEY")

#         headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Basic {api_key}"
#         }

#         response = requests.post(url, json=payload, headers=headers)
#         print(response)
#         print(response.text)
#         data = response.json()
#         print(data)


#         return Response(data)
