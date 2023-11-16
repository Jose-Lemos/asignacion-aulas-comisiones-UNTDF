from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import ListView
from app.models import Comision, Asignacion, Aula
from django.db.models import Q

class ComisionesSinAsignarView(ListView):
    model = Comision
    template_name = 'comisiones_sin_asignar.html'
    context_object_name = "comisiones"
    paginate_by = 30

    def get_queryset(self):
        txt_buscador = self.request.GET.get("buscador")

        if txt_buscador:
            Contenidos = Comision.objects.filter(
                Q(nombre__icontains = txt_buscador)|
                Q(materia__nombre__icontains = txt_buscador)
                )
        else:
            comisiones = Comision.objects.all()
            # Obtener las comisiones asignadas
            comisiones_asignadas = Asignacion.objects.values_list('comision_bh__comision', flat=True)
            # Filtrar las comisiones que no han sido asignadas
            comisiones_no_asignadas = comisiones.exclude(nombre__in=comisiones_asignadas)
            Contenidos = comisiones_no_asignadas
        
        return Contenidos


    """def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las comisiones
        comisiones = Comision.objects.all()
        # Obtener las comisiones asignadas
        comisiones_asignadas = Asignacion.objects.values_list('comision_bh__comision', flat=True)
        # Filtrar las comisiones que no han sido asignadas
        comisiones_no_asignadas = comisiones.exclude(nombre__in=comisiones_asignadas)
        context['comisiones'] = comisiones_no_asignadas


        ###
        for p in Aula.objects.raw(
                                  select *
                                  from App_Aula
                                  
                                  ): print({})
        ###
                                  
    


        return context"""