# Generated by Django 4.2.1 on 2023-07-16 14:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0012_transactiondetail_session_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="transactiondetail",
            name="mail_sent",
            field=models.BooleanField(default=False),
        ),
    ]
