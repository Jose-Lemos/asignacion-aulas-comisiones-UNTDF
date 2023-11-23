from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
 


class AsignarAutomaticamenteView(TemplateView):
    template_name = 'asignar_automaticamente.html'
  
    # ASIGNACIÓN DE AULAS, MODULARIZAR #
    def get(self, request, *args, **kwargs):
        
        # Con .raw() da igual qué clase de use del modelo, es indistinto
        comisiones_sin_asignar = Comision.objects.raw("""
            select distinct ac.*
            from app_comision_bh acb 
            inner join app_comision ac on acb.comision_id = ac.nombre
            where acb.id not in (
                select comision_bh_id 
                from app_asignacion aa 
            )
            order by ac.cant_insc desc -- Con esto ya le estamos dando prioridad a las comisiones con mayor cantidad de inscriptos
        """)

        for c in comisiones_sin_asignar: 
            # print(c)

            ############################
            # Caso preferencia de Aula:
            ############################
            espacio_aula_comision = Espacio_Aula.objects.raw(f"""
                select distinct aea.*
                from app_espacio_aula aea 
                inner join app_comision ac on ac.aula_exclusiva_id = aea.id
                where ac.id = { c.id }
            """)[0:1] # De todas maneras debería traer una única fila
            quiere_aula_exclusiva=False
            if len(espacio_aula_comision) > 0: quiere_aula_exclusiva=True
            
            ############################
            # Caso herramientas Comision:
            ############################
            herramienta_comision = Comision.objects.raw(f"""
                select *
                from app_comision ac 
                inner join app_comision_preferencias acp on ac.id = acp.comision_id  
                where ac.id = { c.id }
            """)
            quiere_herramienta=False
            if len(herramienta_comision) > 0: quiere_herramienta=True

            # Franjas horarias de comisiones sin asignar:
            bhs_sin_asignar = Comision_BH.objects.filter(comision_id=c.nombre)
            
            for bh in bhs_sin_asignar:
                # print(bh)
                
                default_query = f"""
                    select ea.id 
                    from app_espacio_aula ea
                    where ea.id not in (
                        select eax.id
                        from app_asignacion ag
                        inner join app_comision_bh cbh on cbh.id = ag.comision_bh_id 
                        inner join app_espacio_aula eax on eax.id = ag.espacio_aula_id 
                        where { bh.hora_ini } between cbh.hora_ini and cbh.hora_fin
                    )
                    and ea.id = (
                        select eax.id
                        from app_espacio_aula eax
                        inner join app_aula ax on ax.id = eax.aula_id 
                        where eax.capacidad_total >= { c.cant_inscriptos }
                        group by eax.nombre_combinado 
                        order by eax.capacidad_total 
                        limit 1
                    ) 
                """

                # FALTA TESTEAR
                if quiere_aula_exclusiva:
                    aula_libre = Espacio_Aula.objects.raw(f"""
                        { default_query }
                        and ea.id = (
                            select eax.id
                            from app_espacio_aula eax
                            inner join app_aula ax on ax.id = eax.aula_id 
                            where ax.id = { bh.comision.materia.carrera.aula_exclusiva }
                        )
                    """)
                elif quiere_herramienta:
                    aula_libre = Espacio_Aula.objects.raw(f"""
                        { default_query }
                        and ea.id = (
                            select eax.id
                            from app_espacio_aula eax
                            inner join app_aula ax on ax.id = eax.aula_id 
                            inner join app_aula_herramientas ah on ah.aula_id = ax.id 
                            inner join app_herramienta h on h.id = ah.herramienta_id 
                            inner join app_comision_preferencias cp on cp.herramienta_id = h.id 
                            inner join app_comision c on c.id = cp.comision_id 
                            where c.nombre = { bh.comision.nombre }
                            limit 1
                        )
                    """)[0:1] # Por si no funciona el limit 1 en la query
                else:
                    aula_libre = Espacio_Aula.objects.raw(f"{ default_query }")
                
                if aula_libre: # INSERT ASIGNACION TABLE
                    # se puede hacer con ORM
                    Asignacion.objects.raw(f"""
                        insert into app_asignacion(comision_bh_id, espacio_aula_id)
                        values ( { bh.id }, { aula_libre.id })
                    """)

        return render(request, self.template_name)

    # def asignar_automaticamente(request):
    #     comisiones_asignadas = 0
    #     comisiones_no_asignadas = 0

    #     comisiones = Comision.objects.all()

    #     for comision in comisiones:
    #         #asignaciones_comision = Comision_BH.objects.filter(comision=comision)

    #         herramientas_necesarias = comision.preferencias.all()
    #         # Obtener las IDs de las asignaciones de Comision_BH para la comisión actual
    #         comision_bh = Comision_BH.objects.filter(comision=comision).first()

    #         if comision_bh:
    #             dia = comision_bh.dia
    #             hora_ini = comision_bh.hora_ini
    #             hora_fin = comision_bh.hora_fin
    #             fecha_ini = comision_bh.fecha_ini
    #             fecha_fin = comision_bh.fecha_fin
    #     # Obtener las IDs de las asignaciones para la comisión actual
    #         ids_asignaciones_comision = Comision_BH.objects.filter(comision=comision).values_list('id', flat=True)

    #     # Filtrar las aulas disponibles excluyendo aquellas que tienen asignaciones que coinciden con las horas de las comisiones
    #         aulas_disponibles = Espacio_Aula.objects.exclude(
    #         asignacion__comision_bh__id__in=Subquery(ids_asignaciones_comision),
    #         asignacion__comision_bh__hora_ini__lte=F('asignacion__comision_bh__hora_fin'),
    #         asignacion__comision_bh__hora_fin__gte=F('asignacion__comision_bh__hora_ini')
    #     )


    #         # Filtrar aulas disponibles que tengan todas las herramientas necesarias
    #         aulas_con_herramientas = list([1])
    #         for aula in aulas_disponibles:
    #             herramientas_aula = aula.aula.herramientas.all() if aula.aula else []
    #             if all(herramienta in herramientas_aula for herramienta in herramientas_necesarias):
            
    #               aulas_con_herramientas.append(aula)


    #         capacidad_requerida = comision.cant_insc
    #         aula_asignada = None

    #         # Filtrar aulas por capacidad
    #         aulas_con_capacidad = aulas_disponibles.filter(capacidad_total__gte=capacidad_requerida)
    #         if aulas_con_capacidad.exists():
    #             # Verificar si el aula tiene las herramientas necesarias
    #             for aula in aulas_con_capacidad:
    #                 herramientas_necesarias = comision.preferencias.all()
    #                 if herramientas_necesarias and aula.aula.herramientas.filter(id__in=herramientas_necesarias.values_list('id', flat=True)).count() == len(herramientas_necesarias):
    #                     aula_asignada = aula
    #                     break

    #         if not aula_asignada:
    #             # Si no se encontró un aula con todas las herramientas necesarias, se elige una por capacidad más cercana
    #             aula_asignada = aulas_disponibles.order_by('capacidad_total').first()

    #         if aula_asignada:
    #             # Verificar si la comisión requiere aula exclusiva
    #             if comision.requiere_aula_exclusiva and comision.materia.first().carrera.aula_exclusiva:
    #                 aula_asignada = comision.materia.first().carrera.aula_exclusiva.aula

    #             # Asignar el aula a la comisión
    #             Asignacion.objects.create(
    #                 espacio_aula=aula_asignada,
    #                 comision_bh = Comision_BH.objects.create(
    #                     comision=comision,
    #                     dia=dia,  # Esto puede ser un str, asegúrate de que sea un str con el formato correcto
    #                     hora_ini=hora_ini,  # Esto también debe ser un str con el formato correcto
    #                     hora_fin=hora_fin,  # Igualmente, un str con el formato correcto
    #                     fecha_ini=fecha_ini,  # Un str con el formato correcto
    #                     fecha_fin=fecha_fin  # También, un str con el formato correcto
    # )
    #             )
    #             comisiones_asignadas += 1
    #         else:
    #             comisiones_no_asignadas += 1

    #     # Mostrar el resultado
    #     return HttpResponse(f'Comisiones asignadas: {comisiones_asignadas}<br>Comisiones no asignadas: {comisiones_no_asignadas}')
