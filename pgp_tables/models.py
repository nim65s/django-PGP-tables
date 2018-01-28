from datetime import datetime
from subprocess import CalledProcessError, call, check_output

from django.db import models
from django.db.models import (BooleanField, CharField, DateField, F, ForeignKey,
                              IntegerField, ManyToManyField, Model, SlugField, TextField)
from django.db.models.aggregates import Count
from django.urls import reverse

# https://tools.ietf.org/html/rfc4880#section-9.1
ALGO = {1: 'RSA', 2: 'RSA', 3: 'RSA', 16: 'ElGamal', 17: 'DSA', 18: 'EC', 19: 'ECDSA', 20: 'ElGamal', 21: 'DH'}


class Key(Model):
    id = CharField(max_length=16, primary_key=True)
    fingerprint = CharField(max_length=40)
    name = CharField(max_length=100)
    comment = CharField(max_length=100, null=True)
    mail = CharField(max_length=100, null=True)
    creation = DateField(null=True)
    expiration = DateField(null=True)
    valid = BooleanField(default=True)
    length = IntegerField(null=True)
    algorithm = IntegerField(null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        ret = f'Clef {self.id} de {self.name}'
        if self.comment is not None:
            ret += f' ({self.comment})'
        if not self.valid:
            ret = 'INVALID ' + ret
        return ret

    def update_infos(self):
        try:
            ret = check_output(['gpg2', '--with-colons', '--fingerprint', self.id])
        except CalledProcessError:
            call(['gpg2', '--recv-key', self.id])
            ret = check_output(['gpg2', '--with-colons', '--fingerprint', self.id])
        ret = [l.split(':') for l in ret.decode().split('\n')]
        for line in ret:
            if line[0] == 'fpr':
                self.fingerprint = line[9]
                break
        for line in ret:
            if line[0] == 'pub':
                self.creation = datetime.fromtimestamp(int(line[5])).date()
                if line[6]:
                    self.expiration = datetime.fromtimestamp(int(line[6])).date()
                if line[1] in 'oidren':  # GnuPG/doc/DETAILS
                    self.valid = False
                if line[2]:
                    self.length = int(line[2])
                if line[3]:
                    self.algorithm = int(line[3])
                break
        for line in ret:
            if line[0] == 'uid' and '<' in line[9] and '>' in line[9]:
                name, mail = line[9].split('<')
                if '(' in name:
                    name, comment = name.split('(')
                    self.comment = comment.strip()[:-1]
                self.name, self.mail = name.strip(), mail[:-1]
                break
        else:
            for line in ret:
                if line[0] == 'uid':
                    name = line[9]
                    if '(' in name:
                        name, comment = name.split('(')
                        self.comment = comment.strip()[:-1]
                    self.name = name.strip()
                    break
            else:
                raise ValueError(f'la clef {self.id} n’a pas de mail, et pas de nom ?')
        self.save()

    def check_signatures(self):
        try:
            ret = check_output(['gpg2', '--list-sigs', self.id]).decode()
        except CalledProcessError:
            call(['gpg2', '--recv-key', self.id])
            ret = check_output(['gpg2', '--list-sigs', self.id]).decode()
        for signature in self.signed_by.filter(sign=False):
            if signature.signer_id in ret:
                signature.sign = True
                signature.save()

    def signatures(self, ksp):
        return [s.sign for s in self.signed.filter(signed__in=ksp.keys.all())]

    def signed_ksp(self, ksp):
        return self.signed.filter(signed__in=ksp.keys.all())

    def signer_ksp(self, ksp):
        return self.signed_by.filter(signer__in=ksp.keys.all())

    def n_signer(self, ksp):
        return self.signed_ksp(ksp).filter(sign=True).count() - 1

    def n_signed(self, ksp):
        return self.signer_ksp(ksp).filter(sign=True).count() - 1

    def to_sign(self, ksp):
        return self.signed_ksp(ksp).filter(sign=False)

    def to_be_signed_by(self, ksp):
        return self.signer_ksp(ksp).filter(sign=False)

    def algorithm_name(self):
        return ALGO[self.algorithm]


class Signature(Model):
    signer = ForeignKey(Key, related_name='signed', on_delete=models.CASCADE)
    signed = ForeignKey(Key, related_name='signed_by', on_delete=models.CASCADE)
    sign = BooleanField(default=False)

    class Meta:
        unique_together = ('signer', 'signed')
        ordering = ['signer', 'signed']

    def __str__(self):
        return f'{self.signer_id} → {self.signed_id}: {self.sign}'

    def reverse(self):
        return Signature.objects.get(signed=self.signer, signer=self.signed)

    def dir(self):
        """ for graphviz """
        fw, bw = self.sign, self.reverse().sign
        if fw and bw:
            return "both"
        if fw:
            return "forward"
        if bw:
            return "back"


class KeySigningParty(Model):
    name = CharField(max_length=40, unique=True)
    slug = SlugField(null=True)
    keys = ManyToManyField(Key)
    absents = ManyToManyField(Key, related_name='absent_to')
    detail = TextField(null=True)
    date = DateField(blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.name} ({self.keys.count()} + {self.absents.count()} clefs)'

    def get_absolute_url(self):
        return reverse('pgp_tables:ksp', kwargs={'slug': self.slug})

    def signatures(self):
        keys = self.keys.all()
        return Signature.objects.filter(signer__in=keys, signed__in=keys)

    def uniq_signatures(self):
        return self.signatures().filter(signer__lt=F('signed'))

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

    def stats(self):
        signatures, count = self.signatures(), self.keys.count()
        sig_now = signatures.filter(sign=True).count() - count
        sig_max = signatures.count() - count
        return sig_now, sig_max, int(100 * sig_now / sig_max)

    def remove_absents(self):
        for key in self.absents.all():
            self.absents.remove(key)
            self.keys.add(key)
        for key in self.keys.all():
            if not key.valid or key.n_signer(self) < 1 or key.n_signed(self) < 1:
                self.keys.remove(key)
                self.absents.add(key)

    def algo_stats(self):
        return sorted([('%s %i' % (ALGO[s['algorithm']], s['length']), s['count']) for s in
                       self.keys.values('algorithm', 'length').annotate(count=Count('algorithm')).order_by()])
