from csv import DictReader
from django.core.management import BaseCommand
from payment.models import ExchangeRate

ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

class Command(BaseCommand):

    help = "loads data from exchange_rate.csv"

    def handle(self, *args, **options):
    
        
        if ExchangeRate.objects.exists():
            print('ExchangeRate data already loaded...exiting.')
            print(ERROR_MESSAGE)
            return
            
        # Show this before loading the data into the database
        print("Loading  data")

        for row in DictReader(open('./exchange_rate.csv')):
            usd_rate=ExchangeRate(country_name=row['COUNTRY NAME'], currency_name=row['CURRENCY NAME'],
                                   country_code=row['COUNTRY CODE'],currency_code=row['CURRENCY CODE'],
                                   usd_exchange_rate=row['EXCHANGE RATE IN USD'],
                                   )  
            usd_rate.save()
        
        print("Data Loaded Successfully")