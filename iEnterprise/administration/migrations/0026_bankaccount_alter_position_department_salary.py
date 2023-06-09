# Generated by Django 4.1.7 on 2023-03-24 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0025_alter_position_department_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='position',
            name='department',
            field=models.CharField(blank=True, choices=[('Appartements', 'Appartements'), ('Génie civil', 'Génie civil'), ('Ferme', 'Ferme')], db_index=True, max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, db_index=True, max_length=200, null=True)),
                ('month', models.CharField(choices=[('Janvier', 'Janvier'), ('Février', 'Février'), ('Mars', 'Mars'), ('Avril', 'Avril'), ('Mai', 'Mai'), ('Juin', 'Juin'), ('Juillet', 'Juillet'), ('Aout', 'Aout'), ('Septembre', 'Septembre'), ('Octobre', 'Octobre'), ('Novembre', 'Novembre'), ('Décembre', 'Décembre')], db_index=True, max_length=20)),
                ('year', models.IntegerField(db_index=True, max_length=4)),
                ('amount', models.FloatField(db_index=True, default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.bankaccount')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.employee')),
            ],
        ),
    ]
