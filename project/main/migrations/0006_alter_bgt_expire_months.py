# Generated by Django 5.1.4 on 2025-01-01 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_rename_expire_days_bgt_expire_months'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bgt',
            name='expire_months',
            field=models.SmallIntegerField(default=30),
        ),
    ]