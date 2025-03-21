# Generated by Django 5.1.6 on 2025-03-01 09:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petgoda', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hotel',
            name='district',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='postal_code',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='province',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='street_address',
        ),
        migrations.RemoveField(
            model_name='hotel',
            name='sub_district',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='country',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='district',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='postal_code',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='province',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='street_address',
        ),
        migrations.RemoveField(
            model_name='usersdetail',
            name='sub_district',
        ),
        migrations.AddField(
            model_name='usersdetail',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='petgoda.location'),
        ),
    ]
