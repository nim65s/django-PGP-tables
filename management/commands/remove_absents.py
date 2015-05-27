# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from gpg.models import KeySigningParty


class Command(BaseCommand):
    help = 'Supprime les absents'

    def handle(self, *args, **options):
        for ksp in KeySigningParty.objects.all():
            ksp.remove_absents()
