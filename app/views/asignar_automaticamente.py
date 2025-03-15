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
                aula_normal = Aula.objects.get(id=comision.aula_exclusiva)
                espacio_aula = Espacio_Aula.objects.filter(aulas=comision.aula_exclusiva).first()
                if aula_normal:
                    Asignacion.objects.create(aula=aula_normal, comision_bh=comision_bh)
                    comisiones_asignadas_algoritmo += 1
                    asignaciones_por_aula_exclusiva += 1
                    continue
                elif espacio_aula:
                    Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh, real=True)
                    comisiones_asignadas_algoritmo += 1
                    asignaciones_por_aula_exclusiva += 1
                    continue
                else:
                    motivos.append("No se encontró un espacio aula para el aula exclusiva.")

            # Obtener aulas disponibles que no estén asignadas en el mismo horario
            aulas_disponibles = Aula.objects.exclude(
                id__in=Asignacion.objects.filter(comision_bh__dia=comision_bh.dia)
                .values_list("aula_id", flat=True)
            )

            grupos_extensibles_disponibles = Espacio_Aula.objects.exclude(
                id__in=Asignacion.objects.filter(comision_bh__dia=comision_bh.dia)
                .values_list("espacio_aula_id", flat=True)
            )

            # Ordenar grupos extensibles disponibles por capacidad total
            grupos_ordenados = sorted(
                grupos_extensibles_disponibles,
                key=lambda esp: esp.capacidad_total(),
                reverse=True
            )

            # Ordenar aulas disponibles por capacidad total
            aulas_ordenadas = aulas_disponibles.order_by('-capacidad')

            asignada = False

            # Intentar asignar por capacidad del aula (+10 de margen)
            for aula in aulas_ordenadas:
                if aula.capacidad + 10 >= comision.cant_insc:
                    Asignacion.objects.create(aula=aula, comision_bh=comision_bh)
                    comisiones_asignadas_algoritmo += 1
                    asignaciones_por_capacidad += 1
                    asignada = True
                    break
            
            # Si no le dio la capacidad a las aulas individuales, consultar por las extensibles
            if not asignada:
                for espacio_aula in grupos_ordenados:
                    if espacio_aula.capacidad_total() + 10 >= comision.cant_insc:
                        Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh, real=True)
                        comisiones_asignadas_algoritmo += 1
                        asignaciones_por_capacidad += 1
                        asignada = True
                        break

            # Si no se asignó por capacidad, intentamos por herramientas
            if not asignada:
                for espacio_aula in aulas_ordenadas:
                    herramientas_aula = set(espacio_aula.herramientas.all())
                    herramientas_comision = set(comision.preferencias.all())

                    if herramientas_comision.issubset(herramientas_aula):
                        Asignacion.objects.create(aula=espacio_aula, comision_bh=comision_bh)
                        comisiones_asignadas_algoritmo += 1
                        asignaciones_por_herramientas += 1
                        asignada = True
                        break

            # Si no se pudo asignar, registrar los motivos
            if not asignada:
                comisiones_no_asignadas_algoritmo += 1
                if not aulas_disponibles.exists():
                    motivos.append("No hay aulas disponibles en el horario solicitado.")
                elif all(esp.capacidad_total() + 10 < comision.cant_insc for esp in aulas_disponibles):
                    motivos.append("No hay aulas con suficiente capacidad.")
                elif not any(set(comision.preferencias.all()).issubset(set(esp.herramientas.all())) for esp in aulas_disponibles):
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




class AsignarAutomaticamenteView(TemplateView):
    template_name = 'asignar_automaticamente.html'
  
    def post(self, request, *args, **kwargs):
        
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
        #Consulta por Comision, pero debería consultar por ComisionBH

        for c in comisiones_sin_asignar: 
            # print(c)

            # BEGIN, es solamente para setear la variable Booleana correspondiente, no me interesa lo que devuelva en sí
            # ---
            ###########################
            # Caso preferencia de Aula:
            ###########################
            espacio_aula_comision = Espacio_Aula.objects.raw(f"""
                select distinct aea.*
                from app_espacio_aula aea 
                inner join app_comision ac on ac.aula_exclusiva_id = aea.id
                where ac.id = { c.id }
            """)[0:1] # De todas maneras debería traer una única fila
            quiere_aula_exclusiva=False
            if len(espacio_aula_comision) > 0: quiere_aula_exclusiva=True
            
            #############################
            # Caso herramientas Comision:
            #############################
            herramienta_comision = Comision.objects.raw(f"""
                select *
                from app_comision ac 
                inner join app_comision_preferencias acp on ac.id = acp.comision_id  
                where ac.id = { c.id }
            """)
            #Le falta prguntar sobre ComisionBH
            quiere_herramienta=False
            if len(herramienta_comision) > 0: quiere_herramienta=True
            # ---
            # END

            # Franjas horarias de comisiones sin asignar:
            bhs_sin_asignar = Comision_BH.objects.filter(comision_id=c.nombre)
            hora_ini = bhs_sin_asignar.hora_ini
            hora_fin = bhs_sin_asignar.hora_fin
            dia = bhs_sin_asignar.dia

            comision = Comision.objects.get(nombre= bhs_sin_asignar.comision_id)
            materia = comision.materia
            cant_insc = comision.cant_insc
            print(comision) 

            print(dia, hora_ini, hora_fin)
            #asignaciones = Asignacion.objects.filter(espacio_aula_id__ = 1)
            aulas = Espacio_Aula.objects.all()

            # Filtrar las asignaciones que están dentro del rango de horario
            asignaciones_en_rango = Asignacion.objects.filter(
                comision_bh_id__dia=dia,
                comision_bh_id__hora_ini__lt=hora_fin,
                comision_bh_id__hora_fin__gt=hora_ini
            )

            # Excluir las aulas que están asignadas en ese rango de horario
            aulas_no_asignadas_rango = aulas.exclude(asignacion__in=asignaciones_en_rango)

            #FIiltro por aulas con mayor capacidad
            aulas_no_asignadas_rango = aulas_no_asignadas_rango.filter(
                capacidad_total__gt = cant_insc - 10
            ).order_by("capacidad_total")

            # Excluir las aulas que están asignadas en ese rango de horario
            


            for bh in bhs_sin_asignar:
                try:
                    # Variables
                    umbral_min = 1 # Cantidad mínima de alumnos inscriptos
                    excedente_permitido = 10 # Cantidad de alumnos por sobre la capacidad del aula, permitidos

                    # Case
                    if quiere_aula_exclusiva:
                        sql_query = f"""
                            select ea.*
                            from app_espacio_aula ea
                            where ea.aula_id in (
                                select ea.aula_id
                                from app_espacio_aula ea 
                                where nombre_combinado in (
                                    select ea.nombre_combinado 
                                    from app_espacio_aula ea
                                    where ea.nombre_combinado not in (
                                        select eax.nombre_combinado
                                        from app_asignacion ag
                                        inner join app_comision_bh cbh on cbh.id = ag.comision_bh_id
                                        inner join app_espacio_aula eax on eax.id = ag.espacio_aula_id
                                        where '{ bh.hora_ini }' between cbh.hora_ini and cbh.hora_fin
                                          and '{ bh.hora_fin }' between cbh.hora_ini and cbh.hora_fin
                                          and cbh.dia = '{ bh.dia }'
                                    )
                                    and ea.nombre_combinado in (
                                        select eax.nombre_combinado
                                        from app_espacio_aula eax
                                        inner join app_aula ax on ax.id = eax.aula_id 
                                        inner join app_aula_herramientas ah on ah.aula_id = ax.id 
                                        inner join app_herramienta h on h.id = ah.herramienta_id 
                                        inner join app_comision_preferencias cp on cp.herramienta_id = h.id 
                                        inner join app_comision c on c.id = cp.comision_id 
                                        where c.nombre = '{ bh.comision.nombre }'
                                          and eax.capacidad_total + { excedente_permitido } >= { c.cant_insc } and { c.cant_insc } > { umbral_min }
                                        order by eax.capacidad_total 
                                    )
                                    order by ea.capacidad_total
                                    limit 1
                                )
                                INTERSECT
                                select aula_id 
                                from app_espacio_aula aea
                            )
                            order by id
                        """
                        aula_libre = Espacio_Aula.objects.raw(sql_query)
                    #
                    elif quiere_herramienta:
                        sql_query = f"""
                            select ea.nombre_combinado 
                            from app_espacio_aula ea
                            where ea.nombre_combinado not in (
                                select eax.nombre_combinado
                                from app_asignacion ag
                                inner join app_comision_bh cbh on cbh.id = ag.comision_bh_id
                                inner join app_espacio_aula eax on eax.id = ag.espacio_aula_id
                                where '{ bh.hora_ini }' between cbh.hora_ini and cbh.hora_fin
                                    and '{ bh.hora_fin }' between cbh.hora_ini and cbh.hora_fin
                                    and cbh.dia = '{ bh.dia }'
                            )
                            and ea.nombre_combinado in (
                                select eax.nombre_combinado
                                from app_espacio_aula eax
                                inner join app_aula ax on ax.id = eax.aula_id
                                where eax.capacidad_total + { excedente_permitido } >= { c.cant_insc } and { c.cant_insc } > { umbral_min }
                                group by eax.nombre_combinado
                            )
                            and ea.nombre_combinado like 
                                '%'|| 
                                (select eax.nombre_combinado from app_espacio_aula eax where aula_id = { c.aula_exclusiva } limit 1) 
                                || '%'
                        """
                        aula_libre = Espacio_Aula.objects.raw(sql_query)
                    else:
                        sql_query = f"""
                            select ea.*
                            from app_espacio_aula ea
                            where ea.aula_id in (
                                select ea.aula_id
                                from app_espacio_aula ea 
                                where nombre_combinado in (
                                    select ea.nombre_combinado 
                                    from app_espacio_aula ea
                                    where ea.nombre_combinado not in (
                                        select eax.nombre_combinado
                                        from app_asignacion ag
                                        inner join app_comision_bh cbh on cbh.id = ag.comision_bh_id
                                        inner join app_espacio_aula eax on eax.id = ag.espacio_aula_id
                                        where '{ bh.hora_ini }' between cbh.hora_ini and cbh.hora_fin
                                          and '{ bh.hora_fin }' between cbh.hora_ini and cbh.hora_fin
                                          and cbh.dia = '{ bh.dia }'
                                    )
                                    and ea.nombre_combinado in (
                                        select eax.nombre_combinado
                                        from app_espacio_aula eax
                                        inner join app_aula ax on ax.id = eax.aula_id
                                        where eax.capacidad_total + { excedente_permitido } >= { c.cant_insc } and { c.cant_insc } > { umbral_min }
                                        group by eax.nombre_combinado
                                    )
                                    order by ea.capacidad_total
                                    limit 1
                                )
                                INTERSECT
                                select aula_id 
                                from app_espacio_aula aea
                            )
                            order by id
                        """
                        aula_libre = Espacio_Aula.objects.raw(sql_query)
                    
                    aula_libre = aulas_no_asignadas_rango
                    # Luego de realizar la consulta correspondiente, consultaremos si hay un aula libre
                    if aula_libre is not None: # INSERT ASIGNACION TABLE
                        # Si es un Aula Combinada, traerá más de un registro. Es necesario bloquear todas las aulas relacionadas a esta combinación para que no sean tenidas en cuenta al momento de consultar por Aulas Libres
                        # print(aula_libre)
                        for a in aula_libre: 
                            # print(a)
                            asignacion = Asignacion(comision_bh_id=bh.id, espacio_aula_id=a.id)
                            print("Asignacion realizada:", asignacion)
                            asignacion.save()
                    #
                    elif c.cant_insc > umbral_min: print(f"{c} Baja cantidad de inscriptos: { c.cant_insc }; umbral: { umbral_min }")
                    #
                    else: print("No se pudo realizar la asignación", bh)
                # 
                except OperationalError as e:
                    print(f"Comision {c}, Error: {e}")
                    # Faltó ver por qué tira el error, "no such column: None" no identificamos por qué fue
            
        return render(request, self.template_name)