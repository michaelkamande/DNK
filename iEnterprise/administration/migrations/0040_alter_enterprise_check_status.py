# Generated by Django 4.1.7 on 2023-03-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0039_alter_enterprise_check_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enterprise',
            name='check_status',
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
    ]