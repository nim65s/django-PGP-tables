# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from gpg.models import Key, KeySigningParty


class KSPKeyDetailView(DetailView):
    model = KeySigningParty
    template_name = 'gpg/key_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super(KSPKeyDetailView, self).get_context_data(**kwargs)
        ctx['key'] = get_object_or_404(Key, id=self.kwargs.get('key_id'))
        return ctx
