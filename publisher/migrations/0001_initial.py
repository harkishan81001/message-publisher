# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-31 06:14
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import jsonfield.fields
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('irn', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('policy', jsonfield.fields.JSONField(default={b'maxRetries': 3})),
            ],
        ),
    ]
