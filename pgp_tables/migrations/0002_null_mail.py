# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-28 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pgp_tables', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='mail',
            field=models.CharField(max_length=100, null=True),
        ),
    ]