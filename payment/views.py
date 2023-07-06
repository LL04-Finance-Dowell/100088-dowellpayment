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
from .models import ExchangeRate
from .serializers import PaymentSerializer,PaypalPaymentLinkSerializer,StripePaymentLinkSerializer
from .supported_currency import stripe_supported_currency, paypal_supported_currency

from .sendmail import send_mail
from datetime import date

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

def processApikey(api_key):
    url = 'https://100105.pythonanywhere.com/api/v1/process-api-key/'
    payload = {
        "api_key" : api_key,
        "api_service_id" : "DOWELL100012"
    }

    response = requests.post(url, json=payload)
    print(response.json())
    return response.json()

class PaypalPayment(APIView):
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"})
    

    def post(self, request,api_key):
        validate = processApikey(api_key)
        try:
            if validate["success"] == False:
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


            elif validate["message"] == "Limit exceeded":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
            
            elif validate["message"] == "API key is inactive":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data
            price = data['price']
            product_name = data['product']
            currency_code = data['currency_code']
            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})
            
            # check if the currency is supported by papal
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': f'{currency_code.upper()}'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/api/success',
                    'cancel_url': 'https://100088.pythonanywhere.com/api/error'
                }
            })


            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                #If the currency is not supported by paypal, convert it to usd before processing.
                exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

                try:
                    usd_rate = exchange_rate_obj[0].usd_exchange_rate
                except:
                    return Response({"message":f" {currency_code}, not a valid currency code."})
                    
                converted_price = price/usd_rate
                
                
                payment = paypalrestsdk.Payment({
                    'intent': 'sale',
                    'payer': {
                        'payment_method': 'paypal'
                    },
                    'transactions': [{
                        'amount': {
                            'total':f"{round(converted_price,2)}" ,
                            'currency': 'USD'
                        },
                        'description': f"{product_name}"
                    }],
                    'redirect_urls': {
                        'return_url': 'https://100088.pythonanywhere.com/api/success',
                        'cancel_url': 'https://100088.pythonanywhere.com/api/error'
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
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})


    def post(self, request, api_key):
        validate = processApikey(api_key)
        print(validate)
        try:
            if validate["success"] == False:
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


            elif validate["message"] == "Limit exceeded":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
            
            elif validate["message"] == "API key is inactive":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

        try:
            today = date.today()
            data = request.data
            price = data['price']
            product = data['product']
            currency_code = data['currency_code']
            
            exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response({"message":f" {currency_code}, not a valid currency code."})

            converted_price = price/usd_rate
            if int(price) < 1:
                return Response({"message":f"The price cannot be {price}, the lowest number acceptable is 1."})
            
            if converted_price < 0.5:
                return Response({"message":f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"})

            try:
                # try if the currency is supported by stripe
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': f'{currency_code.lower()}',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(price) * 100}",
                },
                'quantity': 1,
                }
                ],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date': today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

            
            except:
                #If the currency is not supported by stripe, convert it to usd before processing.
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(converted_price)*100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
    


#Generate Payment Link
class PaypalPaymentLink(APIView):
    @swagger_auto_schema(request_body=PaypalPaymentLinkSerializer,responses={200: "checkout url"})
    def post(self, request, api_key):
        validate = processApikey(api_key)
        try:
            if validate["success"] == False:
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


            elif validate["message"] == "Limit exceeded":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
            
            elif validate["message"] == "API key is inactive":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

        try:
            data = request.data
            client_id = data['paypal_client_id']
            client_secret = data['paypal_secret_key']
            price = data['price']
            product_name = data['product']
            currency_code = data['currency_code']

            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})

            paypalrestsdk.configure({
                'mode': 'sandbox',
                'client_id': client_id,
                'client_secret': client_secret
            })

            # check if the currency is supported by papal
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': f'{currency_code.upper()}'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/api/success',
                    'cancel_url': 'https://100088.pythonanywhere.com/api/error'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                #If the currency is not supported by paypal, convert it to usd before processing.
                exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

                try:
                    usd_rate = exchange_rate_obj[0].usd_exchange_rate
                except:
                    return Response({"message":f" {currency_code}, not a valid currency code."})
                    
                converted_price = price/usd_rate
                
                payment = paypalrestsdk.Payment({
                    'intent': 'sale',
                    'payer': {
                        'payment_method': 'paypal'
                    },
                    'transactions': [{
                        'amount': {
                            'total':f"{round(converted_price,2)}" ,
                            'currency': 'USD'
                        },
                        'description': f"{product_name}"
                    }],
                    'redirect_urls': {
                        'return_url': 'https://100088.pythonanywhere.com/api/success',
                        'cancel_url': 'https://100088.pythonanywhere.com/api/error'
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
    @swagger_auto_schema(request_body=StripePaymentLinkSerializer,responses={200: 'checkout url'})

    def post(self, request, api_key):
        validate = processApikey(api_key)
        try:
            if validate["success"] == False:
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)


            elif validate["message"] == "Limit exceeded":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
            
            elif validate["message"] == "API key is inactive":
                return Response({'message':validate["message"]},status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':f"api_service_id: {validate['api_service_id']}"},status = status.HTTP_400_BAD_REQUEST)

        try:
            today = date.today()
            data = request.data
            stripe_key = data['stripe_key']
            stripe.api_key = stripe_key
            price = data['price']
            product = data['product']
            currency_code = data['currency_code']

            exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response({"message":f" {currency_code}, not a valid currency code."})

            converted_price = price/usd_rate
            
            if int(price) < 1:
                return Response({"message":f"The price cannot be {price}, the lowest number acceptable is 1."})
            
            if converted_price < 0.5:
                return Response({"message":f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"})
            
            try:
                # try if the currency is supported by stripe 
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': f'{currency_code.lower()}',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(price) * 100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

            except:
                #If the currency is not supported by stripe, convert it to usd before processing.
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(converted_price)*100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
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
        payment_info = event['data']['object']['charges']['data'][0]
        amount = (payment_info['amount'])/100
        currency = payment_info['currency'].upper()
        name = payment_info['billing_details']['name']
        email = payment_info['billing_details']['email']
        desc = payment_info['metadata']['description']
        date = payment_info['metadata']['date']
        city = payment_info['billing_details']['address']['city']
        state = payment_info['billing_details']['address']['state']
        address = payment_info['billing_details']['address']['line1']
        postal_code = payment_info['billing_details']['address']['postal_code']
        country_code = payment_info['billing_details']['address']['country']
        order_id = payment_info['payment_intent']
        payment_method = "Stripe"

        res = send_mail(amount,currency,name,email,desc,date,city,address,postal_code,order_id,payment_method)

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
    date = event_body["create_time"].split("T")[0]
    info = event_body['resource']['payer']
    name = info['payer_info']['shipping_address']['recipient_name']
    email = info['payer_info']['email']
    address = info['payer_info']['shipping_address']['line1']
    city = info['payer_info']['shipping_address']['city']
    state = info['payer_info']['shipping_address']['state']
    postal_code = info['payer_info']['shipping_address']['postal_code']
    country_code = info['payer_info']['shipping_address']['country_code']
    
    transaction_info = event_body['resource']['transactions'][0]
    amount = transaction_info['amount']['total']
    currency = transaction_info['amount']['currency']
    order_id = info['payer_info']['payer_id']
    desc = transaction_info['description']
    payment_method = "Paypal"

    res = send_mail(amount,currency,name,email,desc,date,city,address,postal_code,order_id,payment_method)





#PAYMENT API FOR DOWELL INTERNAL TEAM

class PaypalPaymentForTeam(APIView):
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: "checkout url"})


    def post(self, request):
        try:
            data = request.data
            price = data['price']
            product_name = data['product']
            currency_code = data['currency_code']
            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})
            
            # check if the currency is supported by papal
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': f'{currency_code.upper()}'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/api/success',
                    'cancel_url': 'https://100088.pythonanywhere.com/api/error'
                }
            })


            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                print("price",price)
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                #If the currency is not supported by paypal, convert it to usd before processing.
                exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

                try:
                    usd_rate = exchange_rate_obj[0].usd_exchange_rate
                except:
                    return Response({"message":f" {currency_code}, not a valid currency code."})
                    
                converted_price = price/usd_rate
                
                
                payment = paypalrestsdk.Payment({
                    'intent': 'sale',
                    'payer': {
                        'payment_method': 'paypal'
                    },
                    'transactions': [{
                        'amount': {
                            'total':f"{round(converted_price,2)}" ,
                            'currency': 'USD'
                        },
                        'description': f"{product_name}"
                    }],
                    'redirect_urls': {
                        'return_url': 'https://100088.pythonanywhere.com/api/success',
                        'cancel_url': 'https://100088.pythonanywhere.com/api/error'
                    }
                })
                # Create the payment
                if payment.create():
                    approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                    print("converted_price",converted_price)
                    return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
                else:
                    return Response({'error': payment.error}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
            



class StripePaymentForTeam(APIView):
    stripe.api_key = stripe_key
    @swagger_auto_schema(request_body=PaymentSerializer,responses={200: 'checkout url'})


    def post(self, request):
        try:
            today = date.today()
            data = request.data
            price = data['price']
            product = data['product']
            currency_code = data['currency_code']
            
            exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response({"message":f" {currency_code}, not a valid currency code."})

            converted_price = price/usd_rate
            if int(price) < 1:
                return Response({"message":f"The price cannot be {price}, the lowest number acceptable is 1."})
            
            if converted_price < 0.5:
                return Response({"message":f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"})

            try:
                # try if the currency is supported by stripe
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': f'{currency_code.lower()}',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(price) * 100}",
                },
                'quantity': 1,
                }
                ],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date': today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

            
            except:
                #If the currency is not supported by stripe, convert it to usd before processing.
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(converted_price)*100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)
    


#Generate Payment Link
class PaypalPaymentLinkForTeam(APIView):
    @swagger_auto_schema(request_body=PaypalPaymentLinkSerializer,responses={200: "checkout url"})
    def post(self, request):
        try:
            data = request.data
            client_id = data['paypal_client_id']
            client_secret = data['paypal_secret_key']
            price = data['price']
            product_name = data['product']
            currency_code = data['currency_code']

            if price <= 0:
                return Response({'message':"price cant be zero or less than zero"})

            paypalrestsdk.configure({
                'mode': 'sandbox',
                'client_id': client_id,
                'client_secret': client_secret
            })

            # check if the currency is supported by papal
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'transactions': [{
                    'amount': {
                        'total':f"{price}" ,
                        'currency': f'{currency_code.upper()}'
                    },
                    'description': f"{product_name}"
                }],
                'redirect_urls': {
                    'return_url': 'https://100088.pythonanywhere.com/api/success',
                    'cancel_url': 'https://100088.pythonanywhere.com/api/error'
                }
            })

            # Create the payment
            if payment.create():
                approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
                return Response({'approval_url': approval_url},status = status.HTTP_200_OK)
            else:
                #If the currency is not supported by paypal, convert it to usd before processing.
                exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

                try:
                    usd_rate = exchange_rate_obj[0].usd_exchange_rate
                except:
                    return Response({"message":f" {currency_code}, not a valid currency code."})
                    
                converted_price = price/usd_rate
                
                payment = paypalrestsdk.Payment({
                    'intent': 'sale',
                    'payer': {
                        'payment_method': 'paypal'
                    },
                    'transactions': [{
                        'amount': {
                            'total':f"{round(converted_price,2)}" ,
                            'currency': 'USD'
                        },
                        'description': f"{product_name}"
                    }],
                    'redirect_urls': {
                        'return_url': 'https://100088.pythonanywhere.com/api/success',
                        'cancel_url': 'https://100088.pythonanywhere.com/api/error'
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

  
class StripePaymentLinkForTeam(APIView):
    @swagger_auto_schema(request_body=StripePaymentLinkSerializer,responses={200: 'checkout url'})
    def post(self, request):
        try:
            today = date.today()
            data = request.data
            stripe_key = data['stripe_key']
            stripe.api_key = stripe_key
            price = data['price']
            product = data['product']
            currency_code = data['currency_code']

            exchange_rate_obj = ExchangeRate.objects.filter(currency_code__iexact=currency_code)

            try:
                usd_rate = exchange_rate_obj[0].usd_exchange_rate
            except:
                return Response({"message":f" {currency_code}, not a valid currency code."})

            converted_price = price/usd_rate
            
            if int(price) < 1:
                return Response({"message":f"The price cannot be {price}, the lowest number acceptable is 1."})
            
            if converted_price < 0.5:
                return Response({"message":f"The price must convert to at least 50 cents. {price} {currency_code} converts to approximately ${round(converted_price,3)}"})
            
            try:
                # try if the currency is supported by stripe 
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': f'{currency_code.lower()}',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(price) * 100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)

            except:
                #If the currency is not supported by stripe, convert it to usd before processing.
                session = stripe.checkout.Session.create(
                line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                    'name': f"{product}",
                    },
                    'unit_amount':f"{int(converted_price)*100}",
                },
                'quantity': 1,
                }],
                mode='payment',
                success_url='https://100088.pythonanywhere.com/api/success',
                cancel_url='https://100088.pythonanywhere.com/api/error',
                billing_address_collection='required',
                payment_intent_data={
                        'metadata': {
                        'description':f"{product}",
                        'date':today
                        }
                    }
                )
                return Response({'approval_url':f"{session.url}"},status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':"something went wrong","error":f"{e}"},status = status.HTTP_400_BAD_REQUEST)


#Testing mail endpoint.
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

    res = send_mail(amount,currency,name,email,desc,date,city,address,postal_code,order_id,payment_method)
    return HttpResponse(res)