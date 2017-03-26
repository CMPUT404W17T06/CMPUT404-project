# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 03:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0006_follow_friendrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteCommentAuthor',
            fields=[
                ('authorId', models.URLField(primary_key=True, serialize=False)),
                ('host', models.URLField()),
                ('displayName', models.CharField(max_length=256)),
                ('github', models.URLField()),
            ],
        ),
    ]