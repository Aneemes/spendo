# Generated by Django 5.1.4 on 2025-03-15 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_incomecategory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='incomecategory',
            old_name='colour_code',
            new_name='color_code',
        ),
    ]
