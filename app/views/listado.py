from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import ListView
from app.models import Comision, Asignacion, Aula, Comision_BH
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

        # ASIGNACIÓN DE AULAS, MODULARIZAR #
        
        # Comisiones sin asignar:
        comisiones_asignadas = Asignacion.objects.values_list('comision_bh__comision', flat=True) # Corregir, tiene que traer las comisiones sin asignar para este cuatrimestread
        comisiones_no_asignadas = comisiones.exclude(nombre__in=comisiones_asignadas)

        for c in comisiones_no_asignadas: 
            # print(c)
            # Franjas horarias de comisiones sin asignar:
            comisiones_bh = Comision_BH.objects.filter(comision_id=c.nombre)
            for cbh in comisiones_bh: 
                # print(cbh)
                # Consultar qué preferencia tiene la comision...
                # Luego: case ___: 1, 2, 3... e incluir las consultas:
                
                # Caso DEFAULT:
                # caso_default = """select ea.id 
                # from app_espacio_aula ea
                # where ea.id not in (
                #     select eax.id
                #     from app_asignacion ag
                #     inner join app_comision_bh cbh on cbh.id = ag.comision_bh_id 
                #     inner join app_espacio_aula eax on eax.id = ag.espacio_aula_id 
                #     where '09:00:00' between cbh.hora_ini and cbh.hora_fin -- { cbh.hora_ini }
                # ) -- and ea.id = ( ... ) -- *1. Control de capacidad
                # -- and *2. Control que corresponda según el caso de prioridad. Ver fotos del grupo.
                # and ea.id = (
                #     select eax.id
                #     from app_espacio_aula eax
                #     inner join app_aula ax on ax.id = eax.aula_id 
                #     where eax.capacidad_total >= 27 -- { comi.cant_inscriptos } 
                #     group by eax.nombre_combinado 
                #     order by eax.capacidad_total 
                #     limit 1
                # ) """

                # Caso Exclusivas:
                # caso_default +
                # """-- Caso Aula Exclusiva:
                # and ea.id = (
                #     select eax.id -- *
                #     from app_espacio_aula eax
                #     inner join app_aula ax on ax.id = eax.aula_id 
                #     where ax.id = 10 -- { cbh.comision.materia.carrera.aula_exclusiva }
                # )"""

                # Caso Preferencias:
                # caso_default +
                # """-- Caso Preferencias (herramientas):
                # and ea.id =
                # (
                #     select eax.id -- *
                #     from app_espacio_aula eax
                #     inner join app_aula ax on ax.id = eax.aula_id 
                #     inner join app_aula_herramientas ah on ah.aula_id = ax.id 
                #     inner join app_herramienta h on h.id = ah.herramienta_id 
                #     inner join app_comision_preferencias cp on cp.herramienta_id = h.id 
                #     inner join app_comision c on c.id = cp.comision_id 
                #     where c.id = 329 -- comision.nombre = { cbh.comision_id }
                #     limit 1
                # ) """
                
                pass
                
        
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