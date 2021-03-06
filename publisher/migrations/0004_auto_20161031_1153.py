# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-31 11:53
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('publisher', '0003_auto_20161031_0623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='irn',
            field=models.CharField(help_text='Identity Resource Name(Unique) !', max_length=20, unique=True, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')]),
        ),
    ]
