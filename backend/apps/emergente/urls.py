from django.urls import path
from .views import BandaEmergenteListCreateView

urlpatterns = [
    path('', BandaEmergenteListCreateView.as_view(), name='emergentes-list-create'),
]
