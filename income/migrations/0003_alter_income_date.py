# Generated by Django 5.1.4 on 2025-03-15 09:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('income', '0002_income_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='income',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
