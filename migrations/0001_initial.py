# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.CharField(max_length=8, serialize=False, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=40)),
                ('slug', models.SlugField(null=True)),
                ('detail', models.TextField(null=True)),
                ('absents', models.ManyToManyField(related_name='absent_to', to='gpg.Key')),
                ('keys', models.ManyToManyField(to='gpg.Key')),
            ],
        ),
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sign', models.BooleanField(default=False)),
                ('signed', models.ForeignKey(related_name='signed_by', to='gpg.Key')),
                ('signer', models.ForeignKey(related_name='signed', to='gpg.Key')),
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
