#-*- coding: utf-8 -*-

from __future__ import unicode_literals

from subprocess import call, check_output

from django.core.urlresolvers import reverse
from django.db.models import Model, CharField, ManyToManyField, ForeignKey, BooleanField, SlugField, TextField


class Key(Model):
    id = CharField(max_length=8, primary_key=True)
    fingerprint = CharField(max_length=40)
    name = CharField(max_length=100)
    mail = CharField(max_length=100)

    class Meta:
        ordering = ['id']

    def __unicode__(self):
        return 'Clef {id} de {name}'.format(**self.__dict__)

    def update_infos(self):
        call(['gpg2', '--recv-key', self.id])
        ret = check_output(['gpg2', '--fingerprint', self.id]).decode('utf-8').split('\n')
        self.fingerprint = ret[1].split('=')[1].replace(' ', '')
        for line in ret[2:]:
            if '<' in line and ']' in line:
                name, mail = line.split(']')[1].split('<')
                break
        else:
            raise ValueError('la clef %s n’a pas de mail ?' % self.id)
        self.name, self.mail = name.strip(), mail[:-1]
        self.save()


    def check_signatures(self):
        ret = check_output(['gpg2', '--list-sigs', self.id]).decode('utf-8')
        for signature in self.signed_by.filter(sign=False):
            if signature.signer_id in ret:
                signature.sign = True
                signature.save()


class Signature(Model):
    signer = ForeignKey(Key, related_name='signed')
    signed = ForeignKey(Key, related_name='signed_by')
    sign = BooleanField(default=False)

    class Meta:
        unique_together = ('signer', 'signed')
        ordering = ['signer', 'signed']

    def __unicode__(self):
        return '{signer_id} → {signed_id}: {sign}'.format(**self.__dict__)


class KeySigningParty(Model):
    name = CharField(max_length=40, unique=True)
    slug = SlugField(null=True)
    keys = ManyToManyField(Key)
    absents = ManyToManyField(Key, related_name='absent_to')
    detail = TextField(null=True)

    def __unicode__(self):
        return '%s (%i + %i clefs)' % (self.name, self.keys.count(), self.absents.count())

    def get_absolute_url(self):
        return reverse('gpg:ksp', kwargs={'slug': self.slug})

    def signatures(self):
        keys = self.keys.all()
        return Signature.objects.filter(signer__in=keys, signed__in=keys)

    def add_keys(self, keys):
        for key_id in keys:
            self.add_key(key_id)

    def add_key(self, key_id):
        key, created = Key.objects.get_or_create(id=key_id)
        if created:
            key.update_infos()
            Signature.objects.get_or_create(signer=key, signed=key, sign=True)
        for other_key in self.keys.all():
            Signature.objects.get_or_create(signer=key, signed=other_key)
            Signature.objects.get_or_create(signed=key, signer=other_key)
        if key not in self.keys.all():
            self.keys.add(key)
            self.save()

    def key_signatures(self, key):
        return [s.sign for s in key.signed.filter(signed__in=self.keys.all())]

    def key_signer(self, key):
        return key.signed.filter(sign=True, signed__in=self.keys.all()).count() - 1

    def key_signed(self, key):
        return key.signed_by.filter(sign=True, signer__in=self.keys.all()).count() - 1

    def stats(self):
        return self.signatures().filter(sign=True).count() - self.keys.count(), self.signatures().count() - self.keys.count()

    def remove_absents(self):
        for key in self.keys.all():
            if self.key_signer(key) < 1 or self.key_signed(key) < 1:
                self.keys.remove(key)
                self.absents.add(key)
