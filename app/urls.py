
from django.contrib import admin

from .views.index import *
from .views.listado import *
from .views.asignar_manualmente import *
from django.urls import path




urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('comisiones-sin-asignar/', ComisionesSinAsignarView.as_view(), name='comisiones-sin-asignar'),
    path('asignar-aula/', AsignarManualmenteView.as_view(), name='asignar-aula'),


]