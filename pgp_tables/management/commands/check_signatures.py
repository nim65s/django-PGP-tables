from subprocess import call

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.management.base import BaseCommand

from pgp_tables.models import Key, KeySigningParty


def all_ksps():
    return KeySigningParty.objects.values_list('slug', flat=True)


class Command(BaseCommand):
    help = 'Vérifie les signatures manquantes'

    def add_arguments(self, parser):
        parser.add_argument('ksp', nargs='?', choices=all_ksps())
        parser.add_argument('-r', '--refresh', action='store_true', help='Refresh Keys')

    def handle(self, *args, **options):
        keys = Key.objects if options['ksp'] is None else KeySigningParty.objects.get(slug=options['ksp']).keys
        if options['refresh']:
            call(['gpg2', '--refresh-keys'] + list(keys.values_list('id', flat=True)))
        for key in keys.all():
            key.check_signatures()

        # Invalidate corresponding caches
        for ksp in [k.slug for k in all_ksps()] if options['ksp'] is None else [options['slug']]
            for template in ['ksp_detail', 'ksp_graph']:
                cache.delete(make_template_fragment_key(template, [ksp])
