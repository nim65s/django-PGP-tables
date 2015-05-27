# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import ListView

from gpg.models import KeySigningParty
from gpg.views import KSPDetailView

urlpatterns = patterns('',
        url(r'^$', ListView.as_view(model=KeySigningParty), name='ksps'),
        url(r'^(?P<slug>[^/]+)$', KSPDetailView.as_view(), name='ksp'),
        )

