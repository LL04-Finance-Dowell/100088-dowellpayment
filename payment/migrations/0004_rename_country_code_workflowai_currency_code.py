# Generated by Django 4.2.1 on 2023-05-25 16:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "payment",
            "0003_rename_price_for_template_doc_workflowai_price_for_template_development_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="workflowai",
            old_name="country_code",
            new_name="currency_code",
        ),
    ]
