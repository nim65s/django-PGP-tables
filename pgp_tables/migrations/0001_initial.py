# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-23 19:34
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('fingerprint', models.CharField(max_length=40)),
                ('name', models.CharField(max_length=100)),
                ('mail', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='KeySigningParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
                ('slug', models.SlugField(null=True)),
                ('detail', models.TextField(null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('absents', models.ManyToManyField(related_name='absent_to', to='pgp_tables.Key')),
                ('keys', models.ManyToManyField(to='pgp_tables.Key')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sign', models.BooleanField(default=False)),
                ('signed',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE, related_name='signed_by', to='pgp_tables.Key')),
                ('signer',
                 models.ForeignKey(
                     on_delete=django.db.models.deletion.CASCADE, related_name='signed', to='pgp_tables.Key')),
            ],
            options={
                'ordering': ['signer', 'signed'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='signature',
            unique_together=set([('signer', 'signed')]),
        ),
    ]
