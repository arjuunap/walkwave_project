# Generated by Django 5.1.3 on 2024-12-21 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_address_created_at_alter_address_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='default_address',
            field=models.BooleanField(default=False),
        ),
    ]
