# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-07 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_auto_20171205_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='R_Course_User_Like',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.PositiveIntegerField()),
                ('course_id', models.PositiveIntegerField()),
            ],
        ),
    ]
