from django.core.management.base import BaseCommand
from pgp_tables.models import KeySigningParty


class Command(BaseCommand):
    help = 'Importe les clefs du Capitole du Libre 2014'

    def handle(self, *args, **options):
        keys = ['089047FE', '382A5C4D', '4653CF28', '552CF98B', '5F4445B5', '682A3916', '6B17EA1E', '72F93B05', '78758817', 'C2AA477E', 'DD999172', 'F3B2CEDE']
        ksp, _ = KeySigningParty.objects.get_or_create(name='Capitole du Libre 2014', slug='CdL14')
        ksp.add_keys(keys)
