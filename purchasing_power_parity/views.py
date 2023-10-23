from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PPPSerializer
from .helper import get_all_currency_and_country, get_all_currency_name, get_ppp_data
import requests
import re


# Create your views here.
def processApikey(api_key):
    url = f"https://100105.pythonanywhere.com/api/v3/process-services/?type=api_service&api_key={api_key}"
    payload = {"service_id": "DOWELL10036"}
    response = requests.post(url, json=payload)
    return response.json()


# FOR DOWELL INTERNAL TEAM


class GetCurrencyNameAndCountryName(APIView):
    def get(self, request):
        try:
            #  call the function to get all the currency name
            res = get_all_currency_and_country()
            return res
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "error": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetPurchasingPowerParity(APIView):
    def get(self, request):
        try:
            #  call the function to get all the currency name
            res = get_all_currency_name()
            return res
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "error": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            data = request.data
            # serialize the input data
            serializer = PPPSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                base_currency = validate_data["base_currency"]
                base_price = validate_data["base_price"]
                base_country = validate_data["base_country"]
                target_country = validate_data["target_country"]
                target_currency = validate_data["target_currency"]

            else:
                errors = serializer.errors
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
            
            try:
                email = data["email"]
            except:
                email = None
            
            if email == None:
                return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "details": "Email Field cannot be empty",
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
            #  call the function to get Purchasing Power Parity
            res = get_ppp_data(
                base_currency, base_price, base_country, target_country, target_currency,email
            )
            return res
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "details": "Invalid Country Name",
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

class SendResponseToClient(APIView):
    def post(self,request):
        try:
            data = request.data
            pattern1 = r"base_price_in_\w+"
            pattern2 = r"calculated_price_in_\w+"
            
            base_price_in_base_country =""
            calculated_price_in_target_country = ""
            for key, value in data.items():
                if re.match(pattern1, key):
                    base_price_in_base_country = value
                    
            for key, value in data.items():
                if re.match(pattern2, key):
                    calculated_price_in_target_country = value
                    
                    
            print("base_price_in_base_country",base_price_in_base_country)
            print("calculated_price_in_target_country",calculated_price_in_target_country)
            
            
            email = data["email"]
            base_currency = data["base_currency"]
            target_currency = data["target_currency"]
            exchange_rate = data["exchange_rate"]
            # base_price_in_base_country = data["base_price_in_base_country"] 
            # calculated_price_in_target_country = data["calculated_price_in_target_country"]
            price_in_base_country = data["price_in_base_country"]
            base_country = data["base_country"]
            target_country = data["target_country"]
            target_price = data["target_price"]
            calculated_price_base_on_ppp = data["calculated_price_base_on_ppp"]
            
            url = "https://100085.pythonanywhere.com/api/email/"

            EMAIL_FROM_WEBSITE = """
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <meta http-equiv="X-UA-Compatible" content="IE=edge">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Samanta Content Evaluator</title>
                        </head>
                        <body>
                            <div style="font-family: Helvetica,Arial,sans-serif;min-width:100px;overflow:auto;line-height:2">
                                <div style="margin:50px auto;width:70%;padding:20px 0">
                                <div style="border-bottom:1px solid #eee">
                                    <a href="#" style="font-size:1.2em;color: #00466a;text-decoration:none;font-weight:600">Dowell UX Living Lab</a>
                                </div>
                                <p style="font-size:1.1em">Base Country : {base_country}</p>
                                <p style="font-size:1.1em">Target Country : {target_country}</p>
                                <p style="font-size:1.1em">Price In Base Country : {price_in_base_country}</p>
                                <p style="font-size:1.1em">Base Price In {base_country} : {base_price_in_base_country},</p>
                                <p style="font-size:1.1em">Calculated Price In {target_country} : {calculated_price_in_target_country}</p>
                                <p style="font-size:1.1em">1 {base_currency} = {exchange_rate} {target_currency}</p>
                                <p style="font-size:1.1em">Target Price : {target_price}</p>
                                <p style="font-size:1.1em">Calculated Price Based On PPP : {calculated_price_base_on_ppp}</p>
                                </div>
                            </div>
                        </body>
                        </html>
                      """
            email_content = EMAIL_FROM_WEBSITE.format(
                base_currency = base_currency,
                target_currency = target_currency,
                exchange_rate=exchange_rate,
                base_country=base_country,
                base_price_in_base_country=base_price_in_base_country,
                target_country=target_country,
                calculated_price_in_target_country=calculated_price_in_target_country,
                price_in_base_country=price_in_base_country,
                target_price=target_price,
                calculated_price_base_on_ppp=calculated_price_base_on_ppp,
            )

            payload = {
                "toname": f"{email}",
                "toemail": f"{email}",
                "subject": "Purchasing Power Parity",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(response.text)
            return Response(
        {
            "success": True,
            "message": "Mail sent successfully"
        },
        status=status.HTTP_200_OK,
    )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "error": f"{e}",
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
       
        
        
        
# FOR PUBLIC USAGE
class GetPublicPurchasingPowerParity(APIView):
    def get(self, request, api_key):
        try:
            # Call the dowell Service key API to verify the user API KEY
            validate = processApikey(api_key)
            print(validate)
            if validate["success"] == False:
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )
            #  call the function to get all the currency name
            res = get_all_currency_name()
            return res
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "error": f"{e}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, api_key):
        try:
            validate = processApikey(api_key)
            print(validate)
            if validate["success"] == False:
                return Response(
                    {"message": validate["message"]}, status=status.HTTP_400_BAD_REQUEST
                )

            data = request.data
            # serialize the input data
            serializer = PPPSerializer(data=data)
            if serializer.is_valid():
                validate_data = serializer.validated_data
                base_currency = validate_data["base_currency"]
                base_price = validate_data["base_price"]
                base_country = validate_data["base_country"]
                target_country = validate_data["target_country"]
                target_currency = validate_data["target_currency"]

            else:
                errors = serializer.errors
                return Response(errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

            #  call the function to get Purchasing Power Parity
            res = get_ppp_data(
                base_currency, base_price, base_country, target_country, target_currency
            )
            return res
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "something went wrong",
                    "details": "Invalid Country Name",
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
