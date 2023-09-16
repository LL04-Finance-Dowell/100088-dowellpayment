from django.shortcuts import render
from django.http import HttpResponseRedirect
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
import requests


from .dowellconnection import (
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
from .stripe_helper import stripe_payment, verify_stripe
from .paypal_helper import paypal_payment, verify_paypal
from .voucher import generate_voucher
import os
from dotenv import load_dotenv
load_dotenv()



import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

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
password =  os.getenv("PASSWORD")

class Success(View):
    template_name = "payment/success.html"

    def get(self, request):
        return render(request, self.template_name)


class Error(View):
    template_name = "payment/error.html"

    def get(self, request):
        return render(request, self.template_name)


# PAYMENT API FOR DOWELL INTERNAL TEAM

"""INITIALIZE STRIPE ENDPOINT TO GENERATE APPROVAL URL AND PAYMENT ID AS RESPONSE"""


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
            )
            return res
        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE STRIPE ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class StripeQrcodePayment(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class PaypalQrcodePayment(APIView):
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
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""VERIFY PAYMENT FOR PAYPAL ENDPOINT BY PROVIDING PAYMENT ID AS THE REQUEST BODY"""


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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE STRIPE ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class WorkflowStripeQrPayment(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class WorkflowPaypalQrPayment(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE STRIPE ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class StripeQrPaymentPublic(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class PaypalQrPaymentPublic(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE STRIPE ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class StripeQrPaymentPublicUse(APIView):
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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


"""INITIALIZE PAYPAL ENDPOINT TO GENERATE QRCODE IMAGE URL AND PAYMENT ID AS RESPONSE"""


class PaypalQrPaymentPublicUse(APIView):
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

PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

class NetPaymentPlaid(APIView):
    def post(self,request):

        request = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            redirect_uri='https://100088.pythonanywhere.com/api/success',
            language='en',
            webhook='https://webhook.example.com',
            user=LinkTokenCreateRequestUser(
                client_user_id="user-id"
            )
        )
        response = client.link_token_create(request)
        print(response)

        return Response({"message":response.to_dict()})
    

class InitializeNetPaymentYapily(APIView):
    def post(self,request):
        print("called")
        # print(user,password)
        data = request.data
        amount = data["amount"]
        currency_code = data["currency_code"]
        bank_id = data["bank_id"]
        country_code = data["country_code"]

        unique_id = uuid.uuid4()
        paymentIdempotencyId = str(unique_id).replace("-","")
        print("paymentIdempotencyId",paymentIdempotencyId)

        
        
        

        url = "https://api.yapily.com/payment-auth-requests"

        query = {
        "raw": "true"
        }
        "modelo-sandbox"
        payload = {
            "forwardParameters":[paymentIdempotencyId],
            "applicationUserId": "john.doe@company.com",
            "institutionId": f"{bank_id}" ,
            "callback": "http://127.0.0.1:8000/api/yapily/create/payment",
            "paymentRequest": {
                "paymentIdempotencyId": f"{paymentIdempotencyId}",
                "amount": {
                "amount": amount,
                "currency": f"{currency_code}"
                },
                "reference": "Bill Payment",
                "type": "DOMESTIC_PAYMENT",
                "payee": {
                "name": "Jane Doe",
                "address": {
                    "country": "GB"
                },
                "accountIdentifications": [
                {
                    "type": "SORT_CODE",
                    "identification": "123456"
                },
                {
                    "type": "ACCOUNT_NUMBER",
                    "identification": "12345678"
                }
                ]    }
            }
            
        }

        headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "psu-id": "string",
        "psu-corporate-id": "string",
        "psu-ip-address": "string"
        }

        response = requests.post(url, json=payload, headers=headers, params=query, auth=(user,password))

        res_data = response.json()
        print(res_data)
        obj = YapilyPaymentId.objects.create(payment_id = paymentIdempotencyId,amount=amount,currency_code=currency_code,bank_id=bank_id)
        
        return Response({"authorisationUrl":res_data["data"]["authorisationUrl"],"qrcode_url":res_data["data"]["qrCodeUrl"]})
    
class CreateNetPaymentYapily(APIView):
    def get(self,request):

        full_url = request.get_full_path()
        paymentIdempotencyId = full_url.split("&")[-1][:-1]
        consent_token = request.GET.get("consent")

        obj = YapilyPaymentId.objects.get(payment_id=paymentIdempotencyId)
        amount = obj.amount
        currency_code = obj.currency_code

        url = "https://api.yapily.com/payments"

        query = {
        "raw": "true"
        }

        payload = {
             "paymentIdempotencyId": f"{paymentIdempotencyId}",
                "amount": {
                "amount": amount,
                "currency": f"{currency_code}"
                },
                "reference": "Bill Payment",
                "type": "DOMESTIC_PAYMENT",
                "payee": {
                "name": "Jane Doe",
                "address": {
                    "country": "GB"
                },
                "accountIdentifications": [
                {
                    "type": "SORT_CODE",
                    "identification": "123456"
                },
                {
                    "type": "ACCOUNT_NUMBER",
                    "identification": "12345678"
                }
                ]    }
        }

        headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "consent":f"{consent_token}",
        "psu-id": "string",
        "psu-corporate-id": "string",
        "psu-ip-address": "string"
        }

        response = requests.post(url, json=payload, headers=headers,params=query, auth=(user,password))
        print("----------------------------------")
        data = response.json()
        print(data)
        redirect_url = f"https://www.google.com/?payment_id={paymentIdempotencyId}"
        response = HttpResponseRedirect(redirect_url)
        return  response
    

        





































class GetAllBank(APIView):
    def get(self,request):
        
        url = "https://api.sandbox.token.io/v2/banks"
        # url = "https://api.token.io/banks"
        
        query = {
             "supportsSinglePayment": "true",
        }
        
        response = requests.get(url,params=query )

        data = response.json()
        print(data)
        
        return Response(data)
    
    
class CreatePayment(APIView):
    def post(self,request):
        
        url = "https://api.sandbox.token.io/v2/payments"
        # url = "https://api.token.io/payments"
       
        
        payload = {
            "initiation": {
                "bankId": "ngp-actv",
                "refId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq", 
                "remittanceInformationPrimary": "RemittancePrimary",
                "remittanceInformationSecondary": "RemittanceSecondary",
                "onBehalfOfId": "c5a863bc-86f2-4418-a26f-25b24c7983c7",
                "amount": {
                "value": "10.23",
                "currency": "EUR"
                },
                "localInstrument": "SEPA",
                "debtor": {
                "memberId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq", 
                "iban": "GB29NWBK60161331926819",
                "bic": "BOFIIE2D",
                "name": "John Smith",
                "ultimateDebtorName": "John Smith",
                "address": {
                    "streetName": "221B",
                    "buildingNumber": "2C",
                    "postCode": "E1 6AN",
                    "townName": "Saint Ives",
                    "country": "United Kingdom"
                }
                },
                "creditor": {
                "memberId": "m:3NU9t2ebPBb38JoGiEVbWxDPrB2z:5zKtXEAq", 
                "iban": "GB29NWBK60161331926819",
                "bic": "BOFIIE2D",
                "name": "Customer Inc.",
                "ultimateCreditorName": "Customer Inc.",
                "address": {
                    "streetName": "221B",
                    "buildingNumber": "2C",
                    "postCode": "E1 6AN",
                    "townName": "Saint Ives",
                    "country": "United Kingdom"
                },
                "bankName": "string"
                },
                "executionDate": "2023-04-29",
                "confirmFunds": False,
                "returnRefundAccount": False,
                "disableFutureDatedPaymentConversion": False,
                "callbackUrl": "https://100088.pythonanywhere.com/api/success",
                "callbackState": "c070b02c-4cca-4ee1-9c1a-537c98ad162e",
                "chargeBearer": "CRED",
                "risk": {
                "psuId": "0000789123",
                "paymentContextCode": "PISP_PAYEE",
                "paymentPurposeCode": "DVPM",
                "merchantCategoryCode": "4812",
                "beneficiaryAccountType": "BUSINESS",
                "contractPresentIndicator": True,
                "beneficiaryPrepopulatedIndicator": True
                }
            },
            "pispConsentAccepted": False,
            "initialEmbeddedAuth": {
                "username": "John Smith"
            }
        }
        api_key = os.getenv("API_KEY")
        print(api_key)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {api_key}"
            }

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()
        print(data)

        
        return Response(data)



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
        
        
    
