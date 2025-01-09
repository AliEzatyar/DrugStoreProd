# Generated by Django 5.1.4 on 2025-01-04 03:38

import datetime
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_bgt_expire_months'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(max_length=255)),
                ('client_id', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('amount', models.IntegerField()),
                ('date', django_jalali.db.models.jDateField(default=datetime.date(2025, 1, 4))),
                ('baqi', models.BooleanField(blank=True, default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='bgt',
            name='date',
            field=django_jalali.db.models.jDateField(default=datetime.date(2025, 1, 4)),
        ),
        migrations.AlterField(
            model_name='sld',
            name='date',
            field=django_jalali.db.models.jDateField(default=datetime.date(2025, 1, 4)),
        ),
    ]