# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.admin import site
from gpg.models import Key, KeySigningParty, Signature

for model in [Key, Signature, KeySigningParty]:
    site.register(model)
