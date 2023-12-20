from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PPPSerializer
from datetime import datetime
from .helper import get_all_currency_name, get_ppp_data,get_latest_rate
import requests
import re
import currencyapicom

# from django_wkhtmltopdf.views import PDFTemplateView
from weasyprint import HTML


# Create your views here.
def processApikey(api_key):
    url = f"https://100105.pythonanywhere.com/api/v3/process-services/?type=api_service&api_key={api_key}"
    payload = {"service_id": "DOWELL10036"}
    response = requests.post(url, json=payload)
    return response.json()


# FOR DOWELL INTERNAL TEAM


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
                base_currency,
                base_price,
                base_country,
                target_country,
                target_currency,
                email,
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
    def post(self, request):
        try:
            data = request.data
            pattern1 = r"base_price_in_\w+"
            pattern2 = r"calculated_price_in_\w+"

            base_price_in_base_country = ""
            calculated_price_in_target_country = ""
            for key, value in data.items():
                if re.match(pattern1, key):
                    base_price_in_base_country = value

            for key, value in data.items():
                if re.match(pattern2, key):
                    calculated_price_in_target_country = value

            print("base_price_in_base_country", base_price_in_base_country)
            print(
                "calculated_price_in_target_country", calculated_price_in_target_country
            )

            email = data["email"]
            base_currency = data["base_currency"]
            base_currency_code =data["base_currency_code"]
            target_currency = data["target_currency"]
            target_currency_code =data["target_currency_code"]
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
                <meta charset="UTF-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                <title>DoWell World Price Indicator</title>
            </head>
            <body
                style="
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                "
            >
                <div style="width: 100%; background-color: #ffffff;">
                <header
                    style="
                    color: #fff;
                    display: flex;
                    text-align: center;
                    justify-content: center;
                    padding: 5px;
                    "
                >
                    <img
                    src="https://dowellfileuploader.uxlivinglab.online/hr/logo-2-min-min.png"
                    height="140px"
                    width="140px"
                    style="display: block; margin: 0 auto;"
                    />
                </header>
                <article style="margin-top: 20px; text-align: center;">
                    <h2>DoWell World Price Indicator</h2>
                </article>

                <main style="padding: 20px;">
                    <section style="margin: 20px;">
                    <p>Hi {email},</p>
                    <p>Result from DoWell World Price Indicator :</p>
                    <p style="text-align: left;">
                        <span style="font-weight: bold; font-size: 1.2rem;"
                        >Base Price in {base_country} : {base_price_in_base_country}</span
                        >
                    </p>
                    <p style="text-align: left;">
                        <span style="font-weight: bold; font-size: 1.2rem;"
                        >Calculated Price in {target_country} : {calculated_price_in_target_country}</span
                        >
                    </p>
                    <p style="font-weight: bold; font-size: 14px;">Detailed information :</p>
                    <ul style="font-size: 14px;">
                        <li>Base Currency : {base_currency}</li>
                        <li>Base Country : {base_country}</li>
                        <li>Target Country : {target_country}</li>
                        <li>Target Price : {target_price}</li>
                        <li>Price In Base Country : {price_in_base_country}</li>
                        <li>Base Price In {base_country} : {base_price_in_base_country}</li>
                        <li>Calculated Price In {target_country} : {calculated_price_in_target_country}</li>
                        <li>Calculated Price Based On PPP : {calculated_price_base_on_ppp}</li>
                        <li>Exchange rate. 1 {base_currency_code} = {exchange_rate} {target_currency_code} </li>
                    </ul>
                    <div style="margin: 20px;">
                        <p>
                        Thank You for using DoWell World Price Indicator, for more queries
                        contact
                        <a href="mailto:dowell@dowellresearch.uk"
                            >dowell@dowellresearch.uk</a
                        >
                        </p>
                        <p>DoWell UX Living Lab Team</p>
                    </div>
                    </section>
                </main>

                <footer
                    style="
                    background-color: #005733;
                    color: #fff;
                    text-align: center;
                    padding: 10px;
                    "
                >
                    <a
                    href="https://www.uxlivinglab.org/"
                    style="
                        text-align: center;
                        color: white;
                        margin-bottom: 20px;
                        padding-bottom: 10px;
                    "
                    >DoWell UX Living Lab</a
                    >
                    <p style="margin-top: 10px; font-size: 13px;">
                    &copy; 2023-All rights reserved.
                    </p>
                </footer>
                </div>
            </body>
            </html>
            """

            email_content = EMAIL_FROM_WEBSITE.format(
                email=email,
                base_currency=base_currency,
                base_currency_code = base_currency_code,
                target_currency_code = target_currency_code,
                target_currency=target_currency,
                exchange_rate=exchange_rate,
                base_country=base_country,
                base_price_in_base_country=base_price_in_base_country,
                target_country=target_country,
                calculated_price_in_target_country=calculated_price_in_target_country,
                price_in_base_country=price_in_base_country,
                target_price=target_price,
                calculated_price_base_on_ppp=calculated_price_base_on_ppp,
            )

            date = datetime.now().strftime('%Y-%m-%d')

            payload = {
                "toname": f"{email}",
                "toemail": f"{email}",
                "subject": f"Result from DoWell World Price Indicator on {date}",
                "email_content": email_content,
            }
            response = requests.post(url, json=payload)
            print(response.text)
            return Response(
                {"success": True, "message": "Mail sent successfully"},
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
        

class ExchangeCurrency(APIView):
    def post(self, request):
        base_price = request.data.get("base_price")
        base_currency = request.data.get("base_currency")
        target_currency = request.data.get("target_currency")
        
        try:
            rate = get_latest_rate(base_currency, target_currency)
            converted_price = round(base_price * rate, 2)  # Round to two decimal places

            return Response({
                "target_price": converted_price,
                "target_currency": target_currency
            })
        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_400_BAD_REQUEST)