from csv import DictReader
from django.core.management import BaseCommand

# Import the model
from payment.models import (
    WorkFlowAI,
    WifiQrcode,
    DigitalQ,
    LogoScan,
    Nps,
    Voc,
    UxLive,
    SocialMediaAutomation,
    LicenseCompatibility,
)


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
        # if WorkFlowAI.objects.exists():
        #     print('workflowAI data already loaded...exiting.')
        #     print(ERROR_MESSAGE)
        #     return

        # Show this before loading the data into the database
        print("Loading  data")

        # Code to load the data into database
        for row in DictReader(open("./Costing for payment api  - WORK FLOW AI.csv")):
            workflow_AI = WorkFlowAI(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
                price_for_100_doc=row["PUBLISHED PRICE FOR 100 DOCUMENT"],
                price_for_1000_doc=row["PUBLISHED PRICE FOR 1000 DOCUMENT"],
                price_for_2000_doc=row["PUBLISHED PRICE FOR 2000 DOCUMENT"],
                price_for_1_to_5_member_doc=row["PUBLISHED FOR 1-5 MEMBER"],
                price_for_6_to_10_member_doc=row["PUBLISHED PRICE  FOR 6-10 MEMBER"],
                price_for_11_to_100_member_doc=row["PUBLISHED PRICE FOR 11-100 MEMBER"],
                price_for_template_development=row[
                    "PUBLISHED PRICE FOR TEMPLATE DEVELOPMENT "
                ],
            )
            workflow_AI.save()

        for row in DictReader(open("./Costing for payment api  - WIFI QR CODE.csv")):
            wifi_qrcode = WifiQrcode(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            wifi_qrcode.save()

        for row in DictReader(open("./Costing for payment api  - DIGITAL Q.csv")):
            digital_q = DigitalQ(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            digital_q.save()

        for row in DictReader(open("./Costing for payment api  - LOGO SCAN .csv")):
            logo_can = LogoScan(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            logo_can.save()

        for row in DictReader(open("./Costing for payment api  - NPS.csv")):
            nps = Nps(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            nps.save()

        for row in DictReader(open("./Costing for payment api  - VOC.csv")):
            voc = Voc(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            voc.save()

        for row in DictReader(open("./Costing for payment api  - UX LIVE.csv")):
            ux_live = UxLive(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            ux_live.save()

        for row in DictReader(
            open("./Costing for payment api  - SOCIAL MEDIA AUTOMATION .csv")
        ):
            social_media_automation = SocialMediaAutomation(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            social_media_automation.save()

        for row in DictReader(
            open("./Costing for payment api  - LICENSE COMPATIBILITY.csv")
        ):
            license_compatibility = LicenseCompatibility(
                country_name=row["Country Name"],
                currency_name=row["CURRENCY NAME"],
                currency_code=row["CURRENCY CODE"],
                price=row["PRICE"],
            )
            license_compatibility.save()
