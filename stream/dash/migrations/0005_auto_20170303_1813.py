# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-03 18:13
from __future__ import unicode_literals

import dash.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0004_auto_20170303_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='uuid',
            field=models.CharField(default=dash.models.uuidHex, max_length=36, primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]
