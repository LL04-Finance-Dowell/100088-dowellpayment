# Generated by Django 4.2.1 on 2023-11-28 06:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wallet", "0029_rename_firstname_userprofile_email_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="firstname",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
