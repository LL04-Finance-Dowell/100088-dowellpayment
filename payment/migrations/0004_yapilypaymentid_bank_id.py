# Generated by Django 4.2.1 on 2023-09-16 22:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0003_rename_user_uuid_yapilypaymentid_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="yapilypaymentid",
            name="bank_id",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
