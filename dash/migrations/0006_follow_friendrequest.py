# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 21:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0005_auto_20170324_0251'),
    ]

    operations = [
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend', models.URLField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follow', to='dash.Author')),
            ],
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requester', models.URLField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('requestee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to='dash.Author')),
            ],
        ),
    ]
