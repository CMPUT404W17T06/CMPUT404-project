# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0006_follow_friendrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='follow',
            name='is_friend',
            field=models.BooleanField(default=False),
        ),
    ]