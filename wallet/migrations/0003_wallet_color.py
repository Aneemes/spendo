# Generated by Django 5.1.4 on 2025-03-15 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_rename_amount_wallet_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='color',
            field=models.CharField(default='#007bff', max_length=7),
        ),
    ]
