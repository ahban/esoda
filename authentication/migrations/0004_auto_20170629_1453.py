# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-29 06:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20170608_0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='corpus_id',
            field=models.CharField(default=b'[false, false, false, false, false, false]', max_length=400),
        ),
    ]