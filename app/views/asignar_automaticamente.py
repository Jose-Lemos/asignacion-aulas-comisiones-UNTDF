from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.db import OperationalError


class AsignarAutomaticamenteViewORM(TemplateView):
    template_name = 'asignar_automaticamente.html'
  
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        #### Asignacion de las comisiones con preferencias de Aulas ####
        ComisionesBH = Comision_BH.objects.all().order_by("comision")

        #Obtener las comisiones asignadas
        comisionesBH_ids_asignadas = Asignacion.objects.values_list('comision_bh', flat=True)
        comisionesBH_no_asignadas = ComisionesBH.exclude(id__in=comisionesBH_ids_asignadas)
        #comisiones_no_asignadas
        comisiones_ids_sin_asignar = comisionesBH_no_asignadas.values_list('comision_id', flat=True)
        comisiones_sin_asignar = Comision.objects.all().filter(nombre__in = comisiones_ids_sin_asignar)

        #print(comisiones_sin_asignar)
        #print("Comi:")
        #print(comi)
        #asignaciones = Asignacion.objects.all()
        comision_con_preferencia_aula = comisiones_sin_asignar.exclude(aula_exclusiva_id__isnull = True)  #Obtenemos las comisiones con prefencias de aulas
        #print(comision_con_preferencia_aula)

        list_names_coms = [str]
        for com in comision_con_preferencia_aula:
            list_names_coms.append(com.nombre)
        comisiones_BH_pref_aula = comisionesBH_no_asignadas.filter(comision_id__in = list_names_coms)    #Obtenemos las BH de las comisiones con preferencias de aulas

        #comision_con_preferencia_aula = comision_con_preferencia_aula.exclude()
        
        #print(comisiones_BH_pref_aula)
        cant_pref_asig = 0
        cant_no_asig = 0
        cant_total_asig = comisiones_BH_pref_aula.count()

        

        print("Total de comisionesBH con Preferencias de Aulas: {0}".format(cant_total_asig))

        for comBH_pref in comisiones_BH_pref_aula:
            aulas = Espacio_Aula.objects.all()  #Obtenemos todos lo espacios aulas
            comision = Comision.objects.get(nombre = comBH_pref.comision_id)
            aula_pref = Espacio_Aula.objects.get(id = comision.aula_exclusiva_id)
            #definimos los atributos para filtrar los rangos de las asignaciones
            dia = comBH_pref.dia
            hora_ini = comBH_pref.hora_ini
            hora_fin = comBH_pref.hora_fin

            asignaciones_en_rango = Asignacion.objects.filter(
                comision_bh_id__dia=dia,
                comision_bh_id__hora_ini__lt=hora_fin,
                comision_bh_id__hora_fin__gt=hora_ini,
            )

            # Excluir las aulas que están asignadas en ese rango de horario, para obtener las aulas disponibles en el rango requerido
            aulas_disponibles_BH = aulas.exclude(asignacion__in=asignaciones_en_rango)
            
            if aulas_disponibles_BH.contains(aula_pref):
                print("Aula: "+ aula_pref.nombre_combinado + " DISPONIBLE!!")
                print("Comision BH: "+ comBH_pref.__str__())
                cant_pref_asig +=1
            else:
                print("Aula: "+ aula_pref.nombre_combinado + " OCUPADA!!")
                print("Comision BH: "+ comBH_pref.__str__())
                cant_no_asig +=1

        
        print("{0} Comisiones Asignadas a las Aulas Preferidas!!".format(cant_pref_asig))
        print("{0} Comisiones NO ASIGNADAS a las Aulas Preferidas!!".format(cant_no_asig))
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
                capacidad_total__gt = cant_insc
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