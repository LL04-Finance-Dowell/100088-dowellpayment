from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
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

class Success(View):
    template_name = 'payment/success.html'

    def get(self, request):
        return render(request, self.template_name)

class Error(View):
    template_name = 'payment/error.html'

    def get(self, request):
        return render(request, self.template_name)

class PaypalPayment(APIView):
    #permission_classes = [HasAPIKey]
    # @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"},
    #                     manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
    #                     description='API Key', type=openapi.TYPE_STRING)])

    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})

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
                    'return_url': 'https://testpayment.onrender.com/success',
                    'cancel_url': 'https://testpayment.onrender.com/error'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
            



class StripePayment(APIView):
    #permission_classes = [HasAPIKey]
    stripe.api_key = stripe_key
    # @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'},
    #                     manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
    #                     description='API Key', type=openapi.TYPE_STRING)])

    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})

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
            success_url='https://testpayment.onrender.com/success',
            cancel_url='https://testpayment.onrender.com/error',
            )
            print(session.url)
            return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
    


#Generate Payment Link
class PaypalPaymentLink(APIView):
    permission_classes = [HasAPIKey]
    @swagger_auto_schema(request_body=PaypalPaymentLinkSerializer,responses={200: "checkout url"},
                        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER,
                        description='API Key', type=openapi.TYPE_STRING)])
    def post(self, request):
        try:
            data = request.data
            client_id = data['paypal_client_id']
            client_secret = data['paypal_secret_key']
            price = data['price']
            product_name = data['product']
            paypalrestsdk.configure({
                'mode': 'sandbox',
                'client_id': client_id,
                'client_secret': client_secret
            })
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
                    'return_url': 'https://testpayment.onrender.com/success',
                    'cancel_url': 'https://testpayment.onrender.com/error'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)

  
class StripePaymentLink(APIView):
    permission_classes = [HasAPIKey]
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
            success_url='https://testpayment.onrender.com/success',
            cancel_url='https://testpayment.onrender.com/error',
            )
            print(session.url)
            return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)




@csrf_exempt
def stripe_webhook(request):
    # Retrieve the event data from the request body
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRETE_KEY', None)  # Replace with your own endpoint secret

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
    if event['type'] == 'payment_intent.succeeded':
        # Process the successful payment event
        #payment_intent = event['data']['object']
        payment_info = event['data']['object']['charges']['data']
        print("..................................")
        print(payment_info)

        # ... handle payment success logic ...

    # Return a response to Stripe to acknowledge receipt of the webhook
    return HttpResponse(status=200)



@csrf_exempt
def paypal_webhook(request):
    if request.method == 'POST':
        # Verify the PayPal webhook signature (optional but recommended)

        # Retrieve the webhook event data
        event_body = json.loads(request.body)
        
        # Process the webhook event based on its type
        event_type = event_body['event_type']
        print("----ALL EVENT TYPE-------------")
        print(event_type)
        if event_type == 'PAYMENTS.PAYMENT.CREATED':
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
    payer_info = event_body['resource']['payer']
    print(payer_info)
    print(".....................................")
    transaction_info = event_body['resource']['transactions']
    print(transaction_info)
    # Perform actions based on the completed payment


# paypal_client_id = os.getenv("PAYPAL_CLIENT_ID",None)
# paypal_secret_key = os.getenv("PAYPAL_SECRET_KEY",None)
