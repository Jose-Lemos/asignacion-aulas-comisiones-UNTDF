from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import Comision_BH
from app.models import Comision, Espacio_Aula, Asignacion
from django.db.models import Q
from django.core.management.base import BaseCommand
 


class AsignarAutomaticamenteView(TemplateView):
    template_name = 'asignar_automaticamente.html'
  
    def asignar_automaticamente(request):
            comisiones_asignadas = 0
            comisiones_no_asignadas = 0

            comisiones = Comision.objects.all()

            for comision in comisiones:
                #asignaciones_comision = Comision_BH.objects.filter(comision=comision)

                herramientas_necesarias = comision.preferencias.all()
                # Obtener las IDs de las asignaciones de Comision_BH para la comisión actual
                comision_bh = Comision_BH.objects.filter(comision=comision).first()

                if comision_bh:
                    dia = comision_bh.dia
                    hora_ini = comision_bh.hora_ini
                    hora_fin = comision_bh.hora_fin
                    fecha_ini = comision_bh.fecha_ini
                    fecha_fin = comision_bh.fecha_fin
            # Obtener las IDs de las asignaciones para la comisión actual
                ids_asignaciones_comision = Comision_BH.objects.filter(comision=comision).values_list('id', flat=True)

            # Filtrar las aulas disponibles excluyendo aquellas que tienen asignaciones que coinciden con las horas de las comisiones
                aulas_disponibles = Espacio_Aula.objects.exclude(
                asignacion__comision_bh__id__in=Subquery(ids_asignaciones_comision),
                asignacion__comision_bh__hora_ini__lte=F('asignacion__comision_bh__hora_fin'),
                asignacion__comision_bh__hora_fin__gte=F('asignacion__comision_bh__hora_ini')
            )


                # Filtrar aulas disponibles que tengan todas las herramientas necesarias
                aulas_con_herramientas = list([1])
                for aula in aulas_disponibles:
                    herramientas_aula = aula.aula.herramientas.all() if aula.aula else []
                    if all(herramienta in herramientas_aula for herramienta in herramientas_necesarias):
                
                      aulas_con_herramientas.append(aula)


                capacidad_requerida = comision.cant_insc
                aula_asignada = None

                # Filtrar aulas por capacidad
                aulas_con_capacidad = aulas_disponibles.filter(capacidad_total__gte=capacidad_requerida)
                if aulas_con_capacidad.exists():
                    # Verificar si el aula tiene las herramientas necesarias
                    for aula in aulas_con_capacidad:
                        herramientas_necesarias = comision.preferencias.all()
                        if herramientas_necesarias and aula.aula.herramientas.filter(id__in=herramientas_necesarias.values_list('id', flat=True)).count() == len(herramientas_necesarias):
                            aula_asignada = aula
                            break

                if not aula_asignada:
                    # Si no se encontró un aula con todas las herramientas necesarias, se elige una por capacidad más cercana
                    aula_asignada = aulas_disponibles.order_by('capacidad_total').first()

                if aula_asignada:
                    # Verificar si la comisión requiere aula exclusiva
                    if comision.requiere_aula_exclusiva and comision.materia.first().carrera.aula_exclusiva:
                        aula_asignada = comision.materia.first().carrera.aula_exclusiva.aula

                    # Asignar el aula a la comisión
                    Asignacion.objects.create(
                        espacio_aula=aula_asignada,
                        comision_bh = Comision_BH.objects.create(
                            comision=comision,
                            dia=dia,  
                            hora_ini=hora_ini,  
                            hora_fin=hora_fin,  
                            fecha_ini=fecha_ini,  
                            fecha_fin=fecha_fin  
        )
                    )
                    comisiones_asignadas += 1
                else:
                    comisiones_no_asignadas += 1

            # Mostrar el resultado
            return HttpResponse(f'Comisiones asignadas: {comisiones_asignadas}<br>Comisiones no asignadas: {comisiones_no_asignadas}')
