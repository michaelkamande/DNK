# Generated by Django 4.1.7 on 2023-03-24 09:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0018_outsourcer_position_outsourcer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enterprise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('legal_form', models.CharField(blank=True, choices=[('Ets', 'Ets'), ('SARL', 'SARL'), ('SARLU', 'SARLU'), ('SAS', 'SAS'), ('SASU', 'SASU'), ('SA', 'SA'), ('', '')], db_index=True, max_length=100, null=True)),
                ('phone', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                ('website', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('address', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('devise', models.CharField(blank=True, choices=[('$', '$'), ('€', '€'), ('Fc', 'Fc'), ('FCFA', 'FCFA')], db_index=True, default='$', max_length=5, null=True)),
                ('format_facture', models.CharField(blank=True, choices=[('A4', 'A4'), ('88mm - Imprimante Thermique', '88mm - Imprimante Thermique')], db_index=True, default='A4', max_length=30, null=True)),
                ('vat', models.FloatField(blank=True, db_index=True, default=0, null=True)),
                ('capital', models.FloatField(blank=True, db_index=True, null=True)),
                ('identification', models.CharField(blank=True, db_index=True, max_length=100, null=True)),
                ('vat_number', models.CharField(blank=True, db_index=True, max_length=20, null=True)),
                ('logo', models.ImageField(db_index=True, default='logo.png', upload_to='logo')),
                ('check_status', models.DateTimeField(blank=True, db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('designation', models.CharField(db_index=True, max_length=100)),
                ('description', models.CharField(blank=True, db_index=True, max_length=500, null=True)),
                ('isTerminated', models.BooleanField(db_index=True, default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='appartment',
            name='tag',
        ),
        migrations.AddField(
            model_name='tenant',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.partner'),
        ),
    ]
