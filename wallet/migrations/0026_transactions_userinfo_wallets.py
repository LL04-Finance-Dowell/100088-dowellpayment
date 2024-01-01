# Generated by Django 4.2.1 on 2023-11-26 21:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0025_alter_paymentinitialazation_price"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transactions",
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
                ("username", models.CharField(max_length=100)),
                ("transaction_type", models.CharField(max_length=100)),
                ("status", models.CharField(blank=True, max_length=10, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("payment_id", models.CharField(blank=True, max_length=10, null=True)),
                ("session_id", models.CharField(blank=True, max_length=10, null=True)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserInfo",
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
                ("username", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Wallets",
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
                ("username", models.CharField(max_length=100)),
                ("balance", models.DecimalField(decimal_places=2, max_digits=100)),
                ("currency", models.CharField(max_length=100)),
            ],
        ),
    ]