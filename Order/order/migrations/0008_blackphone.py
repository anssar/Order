# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-05 21:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20170311_1227'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlackPhone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=128)),
            ],
        ),
    ]
