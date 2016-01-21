from django.conf.urls import url
from django.views.generic import DetailView, ListView

from .models import KeySigningParty
from .views import KSPKeyDetailView

app_name = 'pgp_tables'
urlpatterns = [
    url(r'^$', ListView.as_view(model=KeySigningParty), name='ksps'),
    url(r'^(?P<slug>[^/]+)$', DetailView.as_view(model=KeySigningParty), name='ksp'),
    url(r'^(?P<slug>[^/]+)/graph$', DetailView.as_view(model=KeySigningParty, template_name_suffix='_graph'),
        name='graph'),
    url(r'^(?P<slug>[^/]+)/(?P<key_id>[^/]+)$', KSPKeyDetailView.as_view(), name='ksp_key'),
]
