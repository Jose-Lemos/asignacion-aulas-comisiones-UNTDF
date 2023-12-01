
from django.contrib import admin



from .views.asignar_automaticamente import *

from .views.index import *
from .views.listado import *
from .views.asignar_manualmente import *
from django.urls import path
from .views.selection import * 
from .views.reporte import *





urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('comisiones-sin-asignar/', ComisionesSinAsignarView.as_view(), name='comisiones-sin-asignar'),
    path('asignar-aula/', AsignarManualmenteView.as_view(), name='asignar-aula'),
    path('aulas-asignadas/<int:pk>/', aulas_asignadas_reporte.as_view(), name='reporte-aulas-asignadas'),
    #path('asignar-aula/<int:comi>/', AsignarManualmenteViewComision.as_view(), name='asignar-aula-comision'),
    #path('asignar-aula/<int:comi>/<int:aula>/', AsignarManualmenteViewComisionAula.as_view(), name='asignar-aula-comision-aula'),
   # path('aula-disponible/', AsignarAutomaticamenteView.as_view(), name='aula-disponible'),
    path('asignar-automaticamente/', AsignarAutomaticamenteView.as_view(), name='asignar-automaticamente'),
    path('seleccionar_aula/', select_aula.as_view(), name='seleccionar-aula'),
    path('seleccionar_comision_BH/', selection_comision_BH.as_view(), name='seleccionar-comision-BH'),
    path('asignar_manual_aula/<int:comBH>/', AsignarManualmenteAula.as_view(), name='asignar-manual-aula'),
]