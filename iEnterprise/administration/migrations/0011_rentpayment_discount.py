# Generated by Django 4.1.7 on 2023-03-21 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0010_rentpayment_cash_rentpayment_change_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentpayment',
            name='discount',
            field=models.FloatField(db_index=True, default=0),
        ),
    ]