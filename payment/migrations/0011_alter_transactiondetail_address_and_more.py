# Generated by Django 4.2.1 on 2023-07-12 18:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0010_transactiondetail_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transactiondetail",
            name="address",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="amount",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="city",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="country_code",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="currency",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="date",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="desc",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="email",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="order_id",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="postal_code",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="transactiondetail",
            name="state",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]