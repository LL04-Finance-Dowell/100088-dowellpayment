from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PPPSerializer
from .helper import get_all_currency_name, get_ppp_data
import requests


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
