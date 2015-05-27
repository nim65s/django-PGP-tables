# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from django.core.management.base import BaseCommand

from gpg.models import KeySigningParty


class Command(BaseCommand):
    help = 'Importe les clefs du FOSDEM 2014'

    def handle(self, *args, **options):
        ksp, _ = KeySigningParty.objects.get_or_create(name='FOSDEM 2015', slug='fosdem15')
        r = requests.get('https://ksp.fosdem.org/2014/files/ksp-fosdem2014.txt')
        r.raise_for_status()
        ksp.add_keys(len([l.split('/')[1].split()[0] for l in r.content.split('\n') if l.startswith('pub')]))
