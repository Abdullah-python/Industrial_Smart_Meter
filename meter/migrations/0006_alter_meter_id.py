# Generated by Django 5.1.7 on 2025-04-25 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meter', '0005_meterdata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meter',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
