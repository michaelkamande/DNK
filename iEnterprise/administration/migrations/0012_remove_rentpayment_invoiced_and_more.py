# Generated by Django 4.1.7 on 2023-03-22 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_rentpayment_discount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentpayment',
            name='invoiced',
        ),
        migrations.RemoveField(
            model_name='rentpayment',
            name='isComplete',
        ),
        migrations.AddField(
            model_name='rentpayment',
            name='label',
            field=models.CharField(blank=True, db_index=True, max_length=500, null=True),
        ),
    ]