import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from gpg.models import KeySigningParty


class Command(BaseCommand):
    help = 'Importe les clefs de net7'

    def handle(self, *args, **options):
        ksp, _ = KeySigningParty.objects.get_or_create(name='Net7', slug='net7')
        r = requests.get('http://www.bde.inp-toulouse.fr/clubs/inp-net/contact.php')
        r.raise_for_status()
        ksp.add_keys([k['id'] for k in BeautifulSoup(r.content).find_all('span', {'class': 'OpenPGP-Key'})])
