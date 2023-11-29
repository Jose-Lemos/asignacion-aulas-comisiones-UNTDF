from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.db import OperationalError



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
            quiere_herramienta=False
            if len(herramienta_comision) > 0: quiere_herramienta=True
            # ---
            # END

            # Franjas horarias de comisiones sin asignar:
            bhs_sin_asignar = Comision_BH.objects.filter(comision_id=c.nombre)
            
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