# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-10-15 11:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0010_city_night_brigadier_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='tarif',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
