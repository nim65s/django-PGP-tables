from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Key, KeySigningParty, Signature

KEYS = 11
SIGNED = 8


class TestKSP(TestCase):
    def test_all(self):
        call_command('test_ksp')

        self.assertEqual(KeySigningParty.objects.count(), 1)
        self.assertEqual(Key.objects.count(), KEYS)
        self.assertEqual(Signature.objects.count(), (KEYS) ** 2)
        self.assertEqual(Signature.objects.filter(sign=True).count(), KEYS)

        call_command('check_signatures')
        self.assertEqual(Signature.objects.filter(sign=True).count(), 64)  # this might change…

        # test Key model
        ksp = KeySigningParty.objects.first()
        first = Key.objects.first()
        me = Key.objects.get(name='Guilhem Saurel')
        self.assertTrue(str(me).startswith('Clef 7D2A'))
        self.assertTrue(str(first).startswith('Clef 0001'))
        self.assertEqual(len(me.signatures(ksp)), KEYS)
        self.assertEqual(me.signed_ksp(ksp).count(), KEYS)
        self.assertEqual(me.signer_ksp(ksp).count(), KEYS)
        self.assertEqual(me.n_signer(ksp), SIGNED)
        self.assertEqual(me.n_signed(ksp), KEYS - 1)
        self.assertEqual(me.to_sign(ksp).count(), KEYS - 1 - SIGNED)
        self.assertEqual(me.to_be_signed_by(ksp).count(), 0)
        self.assertEqual(me.algorithm_name(), 'RSA')

        # test KSP model
        self.assertEqual(str(ksp), 'KSP de test (11 + 0 clefs)')
        self.assertEqual(ksp.signatures().count(), KEYS ** 2)
        self.assertEqual(ksp.uniq_signatures().count(), KEYS * (KEYS - 1) / 2)
        self.assertEqual(ksp.stats(), (53, 110, 48))  # This might change…
        self.assertEqual(ksp.algo_stats(), [('DSA 3072', 2), ('RSA 2048', 1), ('RSA 4096', 8)])  # This might change…
        call_command('remove_absents')
        self.assertEqual(str(ksp), 'KSP de test (9 + 2 clefs)')

        # test Signature model
        signature = Signature.objects.get(signer=first, signed=me)
        self.assertEqual(str(signature), '00018C22381A7594 → 7D2ACDAF4653CF28: True')
        self.assertEqual(signature.reverse(), Signature.objects.get(signer=me, signed=first))
        self.assertEqual(signature.dir(), 'forward')

        # test views
        req = self.client.get(ksp.get_absolute_url())
        self.assertEqual(req.status_code, 200)
        req = self.client.get(reverse('pgp_tables:ksp_key', args=[ksp.slug, me.id]))
        self.assertEqual(req.status_code, 200)

        # test management commands
