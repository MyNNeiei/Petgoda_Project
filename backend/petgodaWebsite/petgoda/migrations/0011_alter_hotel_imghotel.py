# Generated by Django 5.1.6 on 2025-03-08 12:17

import petgoda.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petgoda', '0010_alter_hotel_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='imgHotel',
            field=models.ImageField(default='hotel_img/default_hotel.jpg', upload_to=petgoda.models.hotel_upload_path),
        ),
    ]
