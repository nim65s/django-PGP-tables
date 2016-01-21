from subprocess import CalledProcessError, call, check_output

from django.core.urlresolvers import reverse
from django.db.models import (F, BooleanField, CharField, DateField, ForeignKey,
                              ManyToManyField, Model, SlugField, TextField)


class Key(Model):
    id = CharField(max_length=8, primary_key=True)
    fingerprint = CharField(max_length=40)
    name = CharField(max_length=100)
    mail = CharField(max_length=100)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return 'Clef {id} de {name}'.format(**self.__dict__)

    def update_infos(self):
        try:
            ret = check_output(['gpg2', '--fingerprint', self.id]).decode('utf-8').split('\n')
        except CalledProcessError:
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


class Signature(Model):
    signer = ForeignKey(Key, related_name='signed')
    signed = ForeignKey(Key, related_name='signed_by')
    sign = BooleanField(default=False)

    class Meta:
        unique_together = ('signer', 'signed')
        ordering = ['signer', 'signed']

    def __str__(self):
        return '{signer_id} → {signed_id}: {sign}'.format(**self.__dict__)

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
        return '%s (%i + %i clefs)' % (self.name, self.keys.count(), self.absents.count())

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
        return signatures.filter(sign=True).count() - count, signatures.count() - count

    def remove_absents(self):
        for key in self.absents.all():
            self.absents.remove(key)
            self.keys.add(key)
        for key in self.keys.all():
            if key.n_signer(self) < 1 or key.n_signed(self) < 1:
                self.keys.remove(key)
                self.absents.add(key)
