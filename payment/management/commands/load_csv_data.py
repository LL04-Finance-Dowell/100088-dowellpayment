from csv import DictReader
from django.core.management import BaseCommand

# Import the model 
from payment.models import WorkFlowAI


ERROR_MESSAGE = """
If you need to reload the data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    # Show this when the user types help
    help = "Loads data from file.csv"

    def handle(self, *args, **options):
    
        # Show this if the data already exist in the database
        if WorkFlowAI.objects.exists():
            print('workflowAI data already loaded...exiting.')
            print(ERROR_MESSAGE)
            return
            
        # Show this before loading the data into the database
        print("Loading workflowAI data")


        #Code to load the data into database
        for row in DictReader(open('./Costing for payment api  - WORK FLOW AI.csv')):
            workflow_AI=WorkFlowAI(country_name=row['Country Name'], currency_name=row['CURRENCY NAME'],
                                   currency_code=row['CURRENCY CODE'],price=row['PRICE'],
                                   price_for_100_doc=row['PUBLISHED PRICE FOR 100 DOCUMENT'],
                                   price_for_1000_doc=row['PUBLISHED PRICE FOR 1000 DOCUMENT'],
                                   price_for_2000_doc=row['PUBLISHED PRICE FOR 2000 DOCUMENT'],
                                   price_for_1_to_5_member_doc=row['PUBLISHED FOR 1-5 MEMBER'],
                                   price_for_6_to_10_member_doc=row['PUBLISHED PRICE  FOR 6-10 MEMBER'],
                                   price_for_11_to_100_member_doc=row['PUBLISHED PRICE FOR 11-100 MEMBER'],
                                   price_for_template_development=row['PUBLISHED PRICE FOR TEMPLATE DEVELOPMENT '])  
            workflow_AI.save()