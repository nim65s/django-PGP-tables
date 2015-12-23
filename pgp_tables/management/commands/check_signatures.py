from subprocess import call

from django.core.management.base import BaseCommand
from pgp_tables.models import Key, KeySigningParty


class Command(BaseCommand):
    help = 'Vérifie les signatures manquantes'

    def add_arguments(self, parser):
        parser.add_argument('ksp', nargs='?', choices=['net7', 'fosdem15', 'CdL14', 'fosdem14'])

    def handle(self, *args, **options):
        keys = Key.objects if options['ksp'] is None else KeySigningParty.objects.get(slug=options['ksp']).keys
        call(['gpg2', '--refresh-keys'] + list(keys.values_list('id', flat=True)))
        for key in keys.all():
            key.check_signatures()
