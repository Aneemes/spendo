# Generated by Django 5.1.4 on 2025-03-24 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_colour_code_incomecategory_color_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensecategory',
            name='title',
            field=models.CharField(max_length=24),
        ),
        migrations.AlterField(
            model_name='incomecategory',
            name='title',
            field=models.CharField(max_length=24),
        ),
    ]
