# Generated by Django 4.2.1 on 2023-09-18 12:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0007_rename_data_yapilypaymentid_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="yapilypaymentid",
            name="status",
            field=models.CharField(
                blank=True, default="Failed", max_length=10, null=True
            ),
        ),
    ]
