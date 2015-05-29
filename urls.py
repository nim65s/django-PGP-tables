# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from gpg.models import KeySigningParty
from gpg.views import KSPKeyDetailView

urlpatterns = patterns('',
        url(r'^$', ListView.as_view(model=KeySigningParty), name='ksps'),
        url(r'^(?P<slug>[^/]+)$', DetailView.as_view(model=KeySigningParty), name='ksp'),
        url(r'^(?P<slug>[^/]+)/(?P<key_id>[^/]+)$', KSPKeyDetailView.as_view(), name='ksp_key'),
        )
