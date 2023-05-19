from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import PaymentSerializer
import os
import json
import requests
import base64
import stripe
from dotenv import load_dotenv

load_dotenv()


stripe_key = os.getenv("STRIPE_KEY",None)
paypal_client_id = os.getenv("PAYPAL_CLIENT_ID",None)
paypal_secret_key = os.getenv("PAYPAL_SECRET_KEY",None)


class PaypalPayment(APIView): 
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"})
    def post(self, request):
        data = request.data
        price = data['price']
        encoded_auth = base64.b64encode((paypal_client_id+':'+paypal_secret_key).encode())
        url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
        headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {encoded_auth.decode()}",
                    "Prefer":"return=representation"
                }
        body={
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",
                            "value": f"{price}"
                        }
                    }
                ]
            }
        response = requests.post(url, headers=headers, data = json.dumps(body))
        res = response.json()
        approve_payment = res['links'][1]['href']
        print(approve_payment)
        return Response({'checkout_url':f"{approve_payment}"})



class StripePayment(APIView):
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})
    def post(self, request):
        data = request.data
        price = data['price']
        calculated_price = int(price) * 100

        # Stripe checkout to pay directly to our account
        session = stripe.checkout.Session.create(
        line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
            'name': 'book',
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