# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 03:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0007_remotecommentauthor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remotecommentauthor',
            name='github',
            field=models.URLField(blank=True, default=''),
        ),
    ]
