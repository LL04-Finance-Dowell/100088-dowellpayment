import os
from csv import DictReader
from typing import Any, Optional
from django.core.management import BaseCommand
from purchasing_power_parity.models import PPPCalculation




from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import re



ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "load data from csv file"

    def handle(self, *args: Any, **options: Any) -> str | None:
        if PPPCalculation.objects.exists():
            print("PPPCalculation data already loaded...exiting.")
            print(ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading  data")

        for row in DictReader(open("./PPP_CALCULATION.csv")):
            ppp_data = PPPCalculation(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                country_code=row["Country Code"],
                currency_code=row["CURRENCY CODE"],
                world_bank_ppp=row["PRICE"],
                usd_exchange_rate=row["EXCHANGE RATE IN USD"],
            )
            ppp_data.save()

        print("Data Loaded Successfully")





#DEVELOPMENT ENVIRONMENT

# SAMPLE_SPREADSHEET_ID = '1o7V941xhnRBuWPGfztoWL5Mt9UGkibbhhXD2tvb0JRs'
# SAMPLE_RANGE_NAME = 'PPP (Base price 1 usd )!A1:G199'

# class Command(BaseCommand):
#     help = "load data from csv file"

#     def handle(self, *args: Any, **options: Any) -> str | None:
#         SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

#         creds = None
#         if os.path.exists('token.json'):
#             creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     'credentials.json', SCOPES)
#                 creds = flow.run_local_server(port=0)
#             with open('token.json', 'w') as token:
#                 token.write(creds.to_json())


#         try:
#             service = build('sheets', 'v4', credentials=creds)

#             # Call the Sheets API
#             sheet = service.spreadsheets()
#             result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                         range=SAMPLE_RANGE_NAME).execute()
#             values = result.get('values', [])

#             if not values:
#                 print('No data found.')
#                 return

#             for row in values[1:]:
#                 print(row)
#                 if len(row) >= 7:  # Make sure the row has enough elements
#                     country_name = row[0]
#                     currency_name = row[1]
#                     country_code = row[2]
#                     currency_code = row[3]
#                     world_bank_ppp = row[4]
#                     usd_exchange_rate = row[5]

#                     # Remove commas and convert to a float
#                     world_bank_ppp = float(re.sub(r'[^\d.]', '', row[4]))
                    
#                     # Remove commas and convert to a float
#                     usd_exchange_rate = float(re.sub(r'[^\d.]', '', row[5]))

#                     ppp_data = PPPCalculation2(
#                         country_name=country_name,
#                         currency_name=currency_name,
#                         country_code=country_code,
#                         currency_code=currency_code,
#                         world_bank_ppp=world_bank_ppp,
#                         usd_exchange_rate=usd_exchange_rate,
#                     )
#                     ppp_data.save()
#                     print()
#                     print("Data saved for:", country_name)
#                 else:
#                     print("Incomplete data for:", row)
#         except HttpError as err:
#             print(err)







# PRODUCTION ENVIRONMENT

# class Command(BaseCommand):
#     help = "load data from csv file"
#     def handle(self, *args, **options):
#         SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
#         SAMPLE_SPREADSHEET_ID = '1o7V941xhnRBuWPGfztoWL5Mt9UGkibbhhXD2tvb0JRs'
#         SAMPLE_RANGE_NAME = 'PPP (Base price 1 usd )!A1:G199'
#         SERVICE_ACCOUNT_KEY_PATH = '/home/nabilah/Desktop/dowell/Payment_API/orgmail-c4daca2e8bab.json'

#         credentials = service_account.Credentials.from_service_account_file('/home/nabilah/Desktop/dowell/Payment_API/orgmail-c4daca2e8bab.json')

        
#         try:
#             service = build('sheets', 'v4', credentials=credentials)

#             sheet = service.spreadsheets()
#             result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                         range=SAMPLE_RANGE_NAME).execute()
#             values = result.get('values', [])

#             if not values:
#                 print('No data found.')
#                 return

#             for row in values:
#                 print(row)
#         except HttpError as err:
#             print(f"An error occurred: {err}")