from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.db import OperationalError
from django.db import models

from django.db.models import Q

class AsignarAutomaticamenteViewORM(TemplateView):
    template_name = 'asignar_automaticamente.html'

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        # Contadores generales
        total_algoritmo = 0
        comisiones_asignadas_algoritmo = 0
        comisiones_no_asignadas_algoritmo = 0
        total_comisiones = Comision_BH.objects.filter(comision__cant_insc__gt=0).count()
        comisiones_asignadas = Asignacion.objects.count()
        comisiones_no_asignadas = total_comisiones - comisiones_asignadas

        # Contadores específicos de tipos de asignación
        asignaciones_por_aula_exclusiva = 0
        asignaciones_por_capacidad = 0
        asignaciones_por_herramientas = 0

        # Registro de motivos de no asignación
        motivos_no_asignacion = []

        # Obtener todas las comisiones sin asignar con al menos un inscrito
        comisiones_bh = Comision_BH.objects.filter(
            ~models.Exists(Asignacion.objects.filter(comision_bh=models.OuterRef('pk'))),
            comision__cant_insc__gt=0
        ).order_by('-comision__cant_insc')

        total_algoritmo = comisiones_bh.count()

        for comision_bh in comisiones_bh:
            comision = comision_bh.comision
            motivos = []

            # Prioridad 1: Aula exclusiva si la tiene definida
            if comision.aula_exclusiva:
                #aula_normal = Aula.objects.get(id=comision.aula_exclusiva)
                espacio_aula = Espacio_Aula.objects.filter(aulas=comision.aula_exclusiva).first()
                # if aula_normal:
                #     Asignacion.objects.create(aula=aula_normal, comision_bh=comision_bh)
                #     comisiones_asignadas_algoritmo += 1
                #     asignaciones_por_aula_exclusiva += 1
                #     continue
                # el
                if espacio_aula:
                    Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh)
                    comisiones_asignadas_algoritmo += 1
                    asignaciones_por_aula_exclusiva += 1
                    continue
                else:
                    motivos.append("No se encontró un espacio aula para el aula exclusiva.")

            # Obtener aulas disponibles que no estén asignadas en el mismo horario
            # aulas_disponibles = Aula.objects.exclude(
            #     id__in=Asignacion.objects.filter(comision_bh__dia=comision_bh.dia)
            #     .values_list("aula_id", flat=True)
            # )

            grupos_extensibles_disponibles = Espacio_Aula.objects.exclude(
                id__in=Asignacion.objects.filter(comision_bh__dia=comision_bh.dia)
                .values_list("espacio_aula_id", flat=True)
            )

            # Ordenar grupos extensibles disponibles por capacidad total
            grupos_ordenados = sorted(
                grupos_extensibles_disponibles,
                key=lambda esp: esp.capacidad_total_calculada(),
                reverse=True
            )

            # Ordenar aulas disponibles por capacidad total
            #aulas_ordenadas = aulas_disponibles.order_by('-capacidad')

            asignada = False

            # Intentar asignar por capacidad del aula (+10 de margen)
            # for aula in aulas_ordenadas:
            #     if aula.capacidad + 10 >= comision.cant_insc:
            #         Asignacion.objects.create(aula=aula, comision_bh=comision_bh)
            #         comisiones_asignadas_algoritmo += 1
            #         asignaciones_por_capacidad += 1
            #         asignada = True
            #         break
            
            # Si no le dio la capacidad a las aulas individuales, consultar por las extensibles
            if not asignada:
                aulas_extensibles = Espacio_Aula.objects.annotate(num_espacios=models.Count('aulas__grupos_extensibles', distinct=True)).filter(num_espacios__gt=1)
                aulas_extensibles_ids = set(aulas_extensibles.values_list('id', flat=True))
                
                # Obtener las aulas ya asignadas desde el modelo Asignacion
                aulas_asignadas = set(Asignacion.objects.values_list('espacio_aula_id', flat=True))
                
                for espacio_aula in grupos_ordenados:
                    if espacio_aula.capacidad_total_calculada() + 10 >= comision.cant_insc:
                        # Verificar si el espacio_aula pertenece a las aulas extensibles
                        if espacio_aula.id not in aulas_extensibles_ids:
                            continue  # Si no es extensible, pasar al siguiente
                        
                        # Verificar si el aula o sus aulas individuales ya están asignadas en la misma banda horaria
                        aulas_ocupadas = set(Asignacion.objects.filter(
                            comision_bh__dia=comision_bh.dia,
                            comision_bh__hora_ini__lt=comision_bh.hora_fin,
                            comision_bh__hora_fin__gt=comision_bh.hora_ini
                        ).values_list('espacio_aula_id', flat=True))
                        aulas_relacionadas = set(Espacio_Aula.objects.filter(aulas__in=espacio_aula.aulas.all()).values_list('id', flat=True))
                        
                        if espacio_aula.id in aulas_ocupadas or any(aula in aulas_ocupadas for aula in aulas_relacionadas):
                            continue  # Si el aula o su extensible están ocupados, pasar al siguiente
                        
                        Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh)
                        comisiones_asignadas_algoritmo += 1
                        asignaciones_por_capacidad += 1
                        asignada = True
                        
                        # Agregar todas las aulas relacionadas a la lista de aulas asignadas
                        aulas_asignadas.update(aulas_relacionadas)
                        
                        break

            # Si no se asignó por capacidad, intentamos por herramientas
            if not asignada:
                for espacio_aula in grupos_ordenados:
                    herramientas_aula = set(espacio_aula.herramientas_totales())
                    herramientas_comision = set(comision.preferencias.all())
                    
                    # Verificar si el aula o su extensible ya están ocupados
                    aulas_ocupadas = set(Asignacion.objects.filter(
                        comision_bh__dia=comision_bh.dia,
                        comision_bh__hora_ini__lt=comision_bh.hora_fin,
                        comision_bh__hora_fin__gt=comision_bh.hora_ini
                    ).values_list('espacio_aula_id', flat=True))
                    aulas_relacionadas = set(Espacio_Aula.objects.filter(aulas__in=espacio_aula.aulas.all()).values_list('id', flat=True))
                    
                    if espacio_aula.id in aulas_ocupadas or any(aula in aulas_ocupadas for aula in aulas_relacionadas):
                        continue  # Si el aula o su extensible están ocupados, pasar al siguiente
                    
                    if herramientas_comision.issubset(herramientas_aula):
                        Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh)
                        comisiones_asignadas_algoritmo += 1
                        asignaciones_por_herramientas += 1
                        asignada = True
                        break

            # Si no se pudo asignar, registrar los motivos
            if not asignada:
                comisiones_no_asignadas_algoritmo += 1
                motivos = []
                if not grupos_extensibles_disponibles.exists():
                    motivos.append("No hay aulas disponibles en el horario solicitado.")
                elif all(esp.capacidad_total_calculada() + 10 < comision.cant_insc for esp in grupos_extensibles_disponibles):
                    motivos.append("No hay aulas con suficiente capacidad.")
                elif not any(set(comision.preferencias.all()).issubset(set(esp.herramientas_totales())) for esp in grupos_extensibles_disponibles):
                    motivos.append("No hay aulas con las herramientas requeridas.")
                
                motivos_no_asignacion.append({
                    "comision": comision.nombre,
                    "motivos": motivos
                })


        comisiones_asignadas = Asignacion.objects.count()
        comisiones_no_asignadas = total_comisiones - comisiones_asignadas

        # Agregar los contadores al contexto para el reporte
        context.update({
            "total_algoritmo": total_algoritmo,
            "comisiones_asignadas_algoritmo": comisiones_asignadas_algoritmo,
            "comisiones_no_asignadas_algoritmo": comisiones_no_asignadas_algoritmo,
            "total_comisiones": total_comisiones,
            "comisiones_asignadas": comisiones_asignadas,
            "comisiones_no_asignadas": comisiones_no_asignadas,
            "asignaciones_por_aula_exclusiva": asignaciones_por_aula_exclusiva,
            "asignaciones_por_capacidad": asignaciones_por_capacidad,
            "asignaciones_por_herramientas": asignaciones_por_herramientas,
            "motivos_no_asignacion": motivos_no_asignacion,
        })

        return self.render_to_response(context)
