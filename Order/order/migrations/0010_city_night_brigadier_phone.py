# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-05 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_auto_20170905_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='night_brigadier_phone',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
