from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import PaymentSerializer,PaypalPaymentLinkSerializer,StripePaymentLinkSerializer

import os
import json
import requests
import base64
import stripe
from dotenv import load_dotenv
import paypalrestsdk
load_dotenv()


stripe_key = os.getenv("STRIPE_KEY",None)
paypalrestsdk.configure({
    'mode': 'sandbox',
    'client_id': os.getenv("PAYPAL_CLIENT_ID",None),
    'client_secret': os.getenv("PAYPAL_SECRET_KEY",None)
})

class PaypalPayment(APIView):
    permission_classes = [HasAPIKey]
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"},
                        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
                        description='API Key', type=openapi.TYPE_STRING)])
    def post(self, request):
        try:
            data = request.data
            price = data['price']
            product_name = data['product']
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': 'USD'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/test/',
                    'cancel_url': 'https://100088.pythonanywhere.com/test/'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':f"{e}"},status = status.HTTP_400_BAD_REQUEST)
            



class StripePayment(APIView):
    permission_classes = [HasAPIKey]
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'},
                        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
                        description='API Key', type=openapi.TYPE_STRING)])
    def post(self, request):
        try:
            data = request.data
            price = data['price']
            product = data['product']
            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})
            calculated_price = int(price) * 100

            # Stripe checkout to pay directly to our account
            session = stripe.checkout.Session.create(
            line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                'name': f"{product}",
                },
                'unit_amount':f"{calculated_price}",
            },
            'quantity': 1,
            }],
            mode='payment',
            success_url='https://100088.pythonanywhere.com/test/',
            cancel_url='https://100088.pythonanywhere.com/test/',
            )
            print(session.url)
            return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f"{e}"},status = status.HTTP_400_BAD_REQUEST)
    


#Generate Payment Link
class PaypalPaymentLink(APIView):
    permission_classes = [HasAPIKey]
    @swagger_auto_schema(request_body=PaypalPaymentLinkSerializer,responses={200: "checkout url"},
                        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
                        description='API Key', type=openapi.TYPE_STRING)])
    def post(self, request):
        try:
            data = request.data
            price = data['price']
            product_name = data['product']
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': 'USD'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/test/',
                    'cancel_url': 'https://100088.pythonanywhere.com/test/'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':f"{e}"},status = status.HTTP_400_BAD_REQUEST)

  
class StripePaymentLink(APIView):
    #permission_classes = [HasAPIKey]
    @swagger_auto_schema(request_body=StripePaymentLinkSerializer,responses={200: 'checkout url'},
                        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
                        description='API Key', type=openapi.TYPE_STRING)])
    def post(self, request):
        try:
            data = request.data
            stripe_key = data['stripe_key']
            stripe.api_key = stripe_key
            price = data['price']
            product = data['product']
            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})
            calculated_price = int(price) * 100

            # Stripe checkout to pay directly to our account
            session = stripe.checkout.Session.create(
            line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                'name': f"{product}",
                },
                'unit_amount':f"{calculated_price}",
            },
            'quantity': 1,
            }],
            mode='payment',
            success_url='https://100088.pythonanywhere.com/test/',
            cancel_url='https://100088.pythonanywhere.com/test/',
            )
            print(session.url)
            return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':f"{e}"},status = status.HTTP_400_BAD_REQUEST)


# paypal_client_id = os.getenv("PAYPAL_CLIENT_ID",None)
# paypal_secret_key = os.getenv("PAYPAL_SECRET_KEY",None)
