# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from gpg.models import Key


class Command(BaseCommand):
    help = 'Vérifie les signatures manquantes'

    def handle(self, *args, **options):
        # call(['gpg2', '--refresh-keys'] + [k.id for k in Key.objects.all()])
        for key in Key.objects.all():
            key.check_signatures()
