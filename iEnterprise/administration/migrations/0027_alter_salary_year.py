# Generated by Django 4.1.7 on 2023-03-24 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0026_bankaccount_alter_position_department_salary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salary',
            name='year',
            field=models.IntegerField(db_index=True, default=2023),
        ),
    ]
