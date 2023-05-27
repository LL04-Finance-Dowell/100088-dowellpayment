from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import WorkflowPaymentSerializer,PaySerializer,OtherPaymentSerializer
from .models import (WorkFlowAI,WifiQrcode,DigitalQ,
                     LogoScan,Nps,Voc,UxLive,SocialMediaAutomation,LicenseCompatibility)
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
    @swagger_auto_schema(request_body=PaySerializer,responses={200: "checkout url"})
    def post(self, request):
        data = request.data
        price = data['price']
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
                'description': 'Payment description'
            }],
            'redirect_urls': {
                'return_url': 'https://100088.pythonanywhere.com/test/',
                'cancel_url': 'https://100088.pythonanywhere.com/test/'
            }
        })

        # Create the payment
        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return Response({'approval_url': approval_url})
        else:
            return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)



class StripePaymentWorkflowAI(APIView):
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=WorkflowPaymentSerializer,responses={200: 'checkout url'})
    def post(self, request):
        try:
            data = request.data
            #price = data['price']
            currency_code = data['currency_code']
            product = data['product']
            quantity = data['quantity']
            query_instance = WorkFlowAI.objects.filter(currency_code=currency_code)
            for instance in query_instance:
                price = getattr(instance,quantity)
                print(price)
                currency = instance.currency_code.lower()
            calculated_price = int(price) * 100
            
            # Stripe checkout to pay directly to our account
            session = stripe.checkout.Session.create(
            line_items=[{
            'price_data': {
                'currency': f"{currency}",
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
            return Response({'checkout_url':f"{session.url}"})
        except Exception as e:
            print(e)
            return Response({"message":f"{e}"},status=status.HTTP_400_BAD_REQUEST)



class StripePaymentOther(APIView):
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=OtherPaymentSerializer,responses={200: 'checkout url'})
    def post(self, request):
        try:
            data = request.data
            #price = data['price']
            currency_code = data['currency_code']
            product = data['product']
            quantity = data['quantity']
            if product == "WifiQrcode":
                query_instance = WifiQrcode.objects.get(currency_code=currency_code)
            elif product == "DigitalQ":
                query_instance = DigitalQ.objects.get(currency_code=currency_code)
            elif product == "LogoScan":
                query_instance = LogoScan.objects.get(currency_code=currency_code)
            elif product == "Nps":
                query_instance = Nps.objects.get(currency_code=currency_code)
            elif product == "Voc":
                query_instance = Voc.objects.get(currency_code=currency_code)
            elif product == "UxLive":
                query_instance = UxLive.objects.get(currency_code=currency_code)
            elif product == "SocialMediaAutomation":
                query_instance = SocialMediaAutomation.objects.get(currency_code=currency_code)
            elif product == "LicenseCompatibility":
                query_instance = LicenseCompatibility.objects.get(currency_code=currency_code)
            else:
                return Response({"message":"Product not available or spelling error"},status=status.HTTP_400_BAD_REQUEST)
            
            price = query_instance.price
            print(price)
            currency = query_instance.currency_code.lower()
            calculated_price = int(price) * 100


            # Stripe checkout to pay directly to our account
            session = stripe.checkout.Session.create(
            line_items=[{
            'price_data': {
                'currency': f"{currency}",
                'product_data': {
                'name': f"{product}",
                },
                'unit_amount':f"{calculated_price}",
            },
            'quantity': quantity,
            }],
            mode='payment',
            success_url='https://100088.pythonanywhere.com/test/',
            cancel_url='https://100088.pythonanywhere.com/test/',
            )
            print(session.url)
            return Response({'checkout_url':f"{session.url}"})
        except Exception as e:
            print(e)
            return Response({"message":f"{e}"},status=status.HTTP_400_BAD_REQUEST)



# class PaypalPayment(APIView): 
#     @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"})
#     def post(self, request):
#         data = request.data
#         price = data['price']
#         encoded_auth = base64.b64encode((paypal_client_id+':'+paypal_secret_key).encode())
#         url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
#         headers = {
#                     "Content-Type": "application/json",
#                     "Authorization": f"Basic {encoded_auth.decode()}",
#                     "Prefer":"return=representation"
#                 }
#         body={
#                 "intent": "CAPTURE",
#                 "purchase_units": [
#                     {
#                         "amount": {
#                             "currency_code": "USD",
#                             "value": f"{price}"
#                         }
#                     }
#                 ]
#             }
#         response = requests.post(url, headers=headers, data = json.dumps(body))
#         res = response.json()
#         approve_payment = res['links'][1]['href']
#         print(approve_payment)
#         return Response({'checkout_url':f"{approve_payment}"})


# paypal_client_id = os.getenv("PAYPAL_CLIENT_ID",None)
# paypal_secret_key = os.getenv("PAYPAL_SECRET_KEY",None)
