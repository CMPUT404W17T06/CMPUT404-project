# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-03 17:37
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0002_auto_20170302_2213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='id',
        ),
        migrations.AlterField(
            model_name='post',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, max_length=36, primary_key=True, serialize=False, verbose_name='id'),
        ),
    ]