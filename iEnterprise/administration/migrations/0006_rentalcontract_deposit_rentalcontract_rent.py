# Generated by Django 4.1.7 on 2023-03-21 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_alter_rentalcontract_end_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalcontract',
            name='deposit',
            field=models.FloatField(blank=True, db_index=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='rentalcontract',
            name='rent',
            field=models.FloatField(blank=True, db_index=True, default=0, null=True),
        ),
    ]
