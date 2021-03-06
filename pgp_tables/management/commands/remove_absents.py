from django.core.cache import cache
from django.core.management.base import BaseCommand

from pgp_tables.models import KeySigningParty


class Command(BaseCommand):
    help = 'Supprime les absents'

    def handle(self, *args, **options):
        for ksp in KeySigningParty.objects.all():
            ksp.remove_absents()

        # Invalidate corresponding caches
        cache.clear()
