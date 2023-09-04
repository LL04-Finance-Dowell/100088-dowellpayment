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

dowell_paypal_mode = os.getenv("DOWELL_PAYPAL_LIVE_MODE")
if dowell_paypal_mode == "True":
    dowell_paypal_url = "https://api-m.paypal.com"
else:
    dowell_paypal_url = "https://api-m.sandbox.paypal.com"


workflow_paypal_mode = os.getenv("WORKFLOW_AI_PAYPAL_LIVE_MODE")
if workflow_paypal_mode == "True":
    workflow_paypal_url = "https://api-m.paypal.com"
else:
    workflow_paypal_url = "https://api-m.sandbox.paypal.com"


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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
            )
            return res

        except Exception as e:
            return Response(
                {"success": False, "message": "something went wrong", "error": f"{e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

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
