from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from .models import Key, KeySigningParty


class KSPKeyDetailView(DetailView):
    model = KeySigningParty
    template_name = 'pgp_tables/keysigningparty_key_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(KSPKeyDetailView, self).get_context_data(**kwargs)
        ctx['key'] = get_object_or_404(Key, id=self.kwargs.get('key_id'))
        return ctx
