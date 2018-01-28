from django.urls import path
from django.views.generic import DetailView, ListView

from .models import KeySigningParty
from .views import KSPKeyDetailView

app_name = 'pgp_tables'
urlpatterns = [
    path('', ListView.as_view(model=KeySigningParty), name='ksps'),
    path('<slug:slug>', DetailView.as_view(model=KeySigningParty), name='ksp'),
    path('<slug:slug>/graph', DetailView.as_view(model=KeySigningParty, template_name_suffix='_graph'), name='graph'),
    path('<slug:slug>/<str:key_id>', KSPKeyDetailView.as_view(), name='ksp_key'),
]
