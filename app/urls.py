
from django.contrib import admin

from .views.index import *
from .views.listado import *
from django.urls import path


urlpatterns = [
    path('', IndexView.as_view(), name='login'),
    path('comisiones-sin-asignar/', ComisionesSinAsignarView.as_view(), name='comisiones-sin-asignar'),


]