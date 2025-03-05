# Generated by Django 5.1.6 on 2025-03-05 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petgoda', '0004_alter_usersdetail_birth_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='location',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='location',
        ),
        migrations.AddField(
            model_name='hotel',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usersdetail',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='Location',
        ),
    ]
