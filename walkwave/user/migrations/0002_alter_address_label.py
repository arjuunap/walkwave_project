# Generated by Django 5.1.3 on 2024-12-20 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='label',
            field=models.CharField(default='home', max_length=50),
        ),
    ]
