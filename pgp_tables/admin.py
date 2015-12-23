from django.contrib.admin import site
from .models import Key, KeySigningParty, Signature

for model in [Key, Signature, KeySigningParty]:
    site.register(model)
