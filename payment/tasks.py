from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.conf import settings
import os
import shutil


def cleanup_qrcodes():
    qr_codes_dir = os.path.join(settings.MEDIA_ROOT, "qrcodes")
    if os.path.exists(qr_codes_dir):
        shutil.rmtree(qr_codes_dir)
        os.makedirs(qr_codes_dir)
        print("Successfully cleaned up QR code images")
    else:
        print("QR code images directory does not exist")


# Create a scheduler
scheduler = BackgroundScheduler()

# Add DjangoJobStore to the scheduler
scheduler.add_jobstore(DjangoJobStore(), "default")

# Schedule the cleanup task to run every 24 hours
scheduler.add_job(
    cleanup_qrcodes,
    trigger=IntervalTrigger(minutes=5),
    id="cleanup_qrcodes",
    name="Cleanup QR Codes",
    replace_existing=True,
)

# Start the scheduler
scheduler.start()
