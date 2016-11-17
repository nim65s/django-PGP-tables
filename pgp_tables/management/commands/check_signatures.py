from subprocess import call

from django.core.management.base import BaseCommand

from pgp_tables.models import Key, KeySigningParty


class Command(BaseCommand):
    help = 'Vérifie les signatures manquantes'

    def add_arguments(self, parser):
        parser.add_argument('ksp', nargs='?', choices=KeySigningParty.objects.values_list('slug', flat=True))
        parser.add_argument('-r', '--refresh', action='store_true', help='Refresh Keys')

    def handle(self, *args, **options):
        keys = Key.objects if options['ksp'] is None else KeySigningParty.objects.get(slug=options['ksp']).keys
        if options['refresh']:
            call(['gpg2', '--refresh-keys'] + list(keys.values_list('id', flat=True)))
        for key in keys.all():
            key.check_signatures()
