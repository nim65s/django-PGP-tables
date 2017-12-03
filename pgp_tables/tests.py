from datetime import date
from subprocess import check_output

from django.test import TestCase

from .models import Key, KeySigningParty, Signature

INITIAL_KEY = '7D2ACDAF4653CF28'
KEYS = 10


class TestKSP(TestCase):
    def test_all(self):
        self.assertEqual(KeySigningParty.objects.count(), 0)
        self.assertEqual(Key.objects.count(), 0)
        self.assertEqual(Signature.objects.count(), 0)

        ksp = KeySigningParty.objects.create(name='KSP de test', slug='test_ksp', date=date.today())
        output = check_output(['gpg', '--with-colons', '--list-sigs', INITIAL_KEY]).decode().split('\n')
        key_ids = sorted(set(l.split(':')[4] for l in output if l.startswith('sig')))[:KEYS]
        ksp.add_keys(key_ids)

        self.assertEqual(KeySigningParty.objects.count(), 1)
        self.assertEqual(Key.objects.count(), KEYS)
        self.assertEqual(Signature.objects.count(), KEYS ** 2)
        self.assertEqual(Signature.objects.filter(sign=True).count(), KEYS)  # this might change…
