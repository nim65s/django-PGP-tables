# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.views.generic import DetailView

from gpg.models import KeySigningParty


class KSPDetailView(DetailView):
    model = KeySigningParty

    def get_context_data(self, **kwargs):
        ctx = super(KSPDetailView, self).get_context_data(**kwargs)
        return ctx
