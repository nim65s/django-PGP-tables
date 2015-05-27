# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand

from gpg.models import KeySigningParty


class Command(BaseCommand):
    help = 'Importe les clefs du FOSDEM 2015'

    def handle(self, *args, **options):
        ksp, _ = KeySigningParty.objects.get_or_create(name='FOSDEM 2015', slug='fosdem15')
        r = requests.get('https://ksp.fosdem.org/keys/')
        r.raise_for_status()
        ksp.add_keys([a['href'][-8:] for a in BeautifulSoup(r.content).find_all('a') if len(a['href']) == 16])
