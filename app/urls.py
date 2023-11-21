
from django.contrib import admin



from .views.asignar_automaticamente import *

from .views.index import *
from .views.listado import *
from .views.asignar_manualmente import *
from django.urls import path





urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('comisiones-sin-asignar/', ComisionesSinAsignarView.as_view(), name='comisiones-sin-asignar'),
    path('asignar-aula/', AsignarManualmenteView.as_view(), name='asignar-aula'),
   # path('aula-disponible/', AsignarAutomaticamenteView.as_view(), name='aula-disponible'),
    path('asignar-automaticamente/', AsignarAutomaticamenteView.as_view(), name='asignar-automaticamente'),


]