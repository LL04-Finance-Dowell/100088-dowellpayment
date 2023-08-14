# Generated by Django 4.2.1 on 2023-07-21 07:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0014_paymentlinktransaction"),
    ]

    operations = [
        migrations.CreateModel(
            name="PubicTransactionDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("payment_id", models.CharField(max_length=200)),
                ("session_id", models.CharField(blank=True, max_length=500, null=True)),
                ("amount", models.CharField(blank=True, max_length=100, null=True)),
                ("currency", models.CharField(blank=True, max_length=100, null=True)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                ("email", models.CharField(blank=True, max_length=100, null=True)),
                ("desc", models.CharField(blank=True, max_length=100, null=True)),
                ("date", models.CharField(blank=True, max_length=100, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("address", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "postal_code",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "country_code",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("order_id", models.CharField(blank=True, max_length=100, null=True)),
                ("status", models.CharField(blank=True, max_length=100, null=True)),
                ("mail_sent", models.BooleanField(default=False)),
            ],
        ),
    ]