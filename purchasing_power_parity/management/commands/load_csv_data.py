from csv import DictReader
from typing import Any, Optional
from django.core.management import BaseCommand
from purchasing_power_parity.models import PPPCalculation



ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""



class Command(BaseCommand):

    help = "load data from csv file"

    def handle(self, *args: Any, **options: Any) -> str | None:

        if PPPCalculation.objects.exists():
            print('PPPCalculation data already loaded...exiting.')
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
                world_bank_ppp=row["WORLD BANK PPP "],
                # usd_exchange_rate=row["EXCHANGE RATE IN USD"],
            )
            ppp_data.save()

        print("Data Loaded Successfully")


