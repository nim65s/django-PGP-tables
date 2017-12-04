from datetime import date
from subprocess import check_output

from django.core.management.base import BaseCommand

from pgp_tables.models import KeySigningParty

INITIAL_KEY = '7D2ACDAF4653CF28'
KEYS = 11


class Command(BaseCommand):
    help = 'Add a test KSP'

    def handle(self, *args, **options):
        ksp = KeySigningParty.objects.create(name='KSP de test', slug='test_ksp', date=date.today())
        output = check_output(['gpg', '--with-colons', '--list-sigs', INITIAL_KEY]).decode().split('\n')
        key_ids = [INITIAL_KEY] + sorted(set(l.split(':')[4] for l in output if l.startswith('sig')))[:KEYS - 1]
        ksp.add_keys(key_ids)
