# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-10 23:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0005_auto_20170310_0227'),
    ]

    operations = [
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('accepted', models.NullBooleanField(default=None)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='github',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='requestee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requestee', to='dash.Author'),
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requester', to='dash.Author'),
        ),
    ]