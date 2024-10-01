from django.db.models import Count, F, Subquery, OuterRef
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from app.models import *
from django.db.models import Q
from django.core.management.base import BaseCommand
from django.db import OperationalError
from django.db import models


class AsignarAutomaticamenteViewORM(TemplateView):
    template_name = 'asignar_automaticamente.html'
  
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        cant_tot_asig_algoritmo = 0
        cant_tot_no_asig_algoritmo = 0

        # Obtener los espacios_aulas que tienen el campo 'nombre_combinado' repetido
        aulas_repetidas = Espacio_Aula.objects.values('nombre_combinado').annotate(num_repeticiones=Count('nombre_combinado')).filter(num_repeticiones__gt=1)
        aul_rep_ids_list = []
        
        for aulas_ext in aulas_repetidas:
            nombre = aulas_ext['nombre_combinado']
            num_repeticiones = aulas_ext['num_repeticiones']
            aulas_con_nombre_repetido = Espacio_Aula.objects.filter(nombre_combinado=nombre)
            print(f"Nombre: {nombre}, Repeticiones: {num_repeticiones}")
            ids_aulas_ext = []
            ids_esp_aula_ext = []
            for esp_au in aulas_con_nombre_repetido:
                ids_aulas_ext.append(esp_au.aula_id)
                ids_esp_aula_ext.append(esp_au.id)
                print(f"ID del objeto: {esp_au.id}")
            print("IDs Aulas:")
            #print(ids_aulas_ext)
            Au_Rep_Ids = {"id": ids_esp_aula_ext,"nombre_combinado": nombre, "repeticiones": num_repeticiones, "ids_aulas":ids_aulas_ext}
            aul_rep_ids_list.append(Au_Rep_Ids)
        print('############------------------->',aul_rep_ids_list, '\n')
        #print(ids_esp_aula_ext)
        #### Asignacion de las comisiones con preferencias de Aulas ####
        ComisionesBH = Comision_BH.objects.all().order_by("comision")

        #Obtener las comisiones BH asignadas
        comisionesBH_ids_asignadas = Asignacion.objects.values_list('comision_bh', flat=True)
        comisionesBH_no_asignadas = ComisionesBH.exclude(id__in=comisionesBH_ids_asignadas)
        #comisiones_no_asignadas
        comisiones_ids_sin_asignar = comisionesBH_no_asignadas.values_list('comision_id', flat=True)
        comisiones_sin_asignar = Comision.objects.all().filter(nombre__in = comisiones_ids_sin_asignar)

        #print(comisiones_sin_asignar)
        #print("Comi:")
        #print(comi)
        #asignaciones = Asignacion.objects.all()
        # Comisiones con Preferencias de Aulas
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
        aulas = Espacio_Aula.objects.all()  #Obtenemos todos lo espacios aulas
        for comBH_pref in comisiones_BH_pref_aula:
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

            if (aula_pref.id in ids_esp_aula_ext):
                print("La comisión Requiere un aula extensible!!")
                nombre_combinado = aula_pref.nombre_combinado
                
            else: 
                print("la comisión NO REQUIERE un aula extensible!!")
            
            if aulas_disponibles_BH.contains(aula_pref):
                print("Aula: "+ aula_pref.nombre_combinado + " DISPONIBLE!!")
                print("Comision BH: "+ comBH_pref.__str__())
                #Asignacion.objects.create(espacio_aula=aula_pref, comision_bh=comBH_pref)
                Asignacion.objects.create(espacio_aula=aula_pref, comision_bh=comBH_pref, real=True)
                    ################################### Verificación de las aulas extensibles ########################
                    ###acá hay que corregir
                    #Au_Rep_Ids = {"id": ids_esp_aula_ext,"nombre_combinado": nombre, "repeticiones": num_repeticiones, "ids_aulas":ids_aulas_ext}
                    #aul_rep_ids_list.append(Au_Rep_Ids)
                asignacion_final = []
                for aurl in aul_rep_ids_list:
                        #print("dict:", aurl)
                        ### verificamos desde el lado de las aulas extensibles con más de una
                    if (aula_pref.id in aurl["id"]):
                        for aula_pref.id in aurl["ids_aulas"]:
                            asignacion_final.append(aurl["id"] + aurl["ids_aulas"])
                        
                        

                        ### verificamos desde el lado de las aulas individuales que se pueden hacer extensibles
                    else: #
                        if(aula_pref.id in aurl["ids_aulas"]):
                            asignacion_final.append(aurl["id"])
                            
                        
                            #Asignacion.create
                        #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                        #for asig in asignacion_final:
                         #   aula_asig = Espacio_Aula.objects.get(id = asig)
                          #  Asignacion.objects.create(espacio_aula=aula_asig, comision_bh=comiBH)
                    #simplificamos la lista para no tener ids repetidos
                asig_final_simple = []
                for asig_f in asignacion_final:
                    for asf in asig_f:
                        if not(asf in asig_final_simple):
                            asig_final_simple.append(asf)
                    #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                for asig in asig_final_simple:
                    aula_pref = Espacio_Aula.objects.get(id = asig)
                    Asignacion.objects.create(espacio_aula=aula_pref, comision_bh=comBH_pref, real=False)    
                print("###################_____________LISTAS-ASIGNACION FINAL:", asignacion_final)
                    #print("asig_final_final", asig_final_final)
                print("asig_final_simple", asig_final_simple)
                print("Asignación Realizada con Éxito")
                cant_pref_asig +=1
                cant_tot_asig_algoritmo +=1
                #FALTA AGREGAR LA VERIFICACIÓN Y ASIGNACIÓN DE LAS AULAS EXTENSIBLES
                ######################################################################### verificacion de las aulas extensibles
            else:
                print("Aula: "+ aula_pref.nombre_combinado + " OCUPADA!!")
                print("Comision BH: "+ comBH_pref.__str__())
                print("NO SE PUDO REALIZAR LA ASIGNACIÓN!")
                cant_no_asig +=1
                cant_tot_no_asig_algoritmo +=1

        
        print("{0} Comisiones Asignadas a las Aulas Preferidas!!".format(cant_pref_asig))
        print("{0} Comisiones NO ASIGNADAS a las Aulas Preferidas!!".format(cant_no_asig))
        #### Fin de Asignaciones de Aulas Preferidas ####

        





        #### Asignar Comisiones con Requerimientos de Herramientas ####
        #Obtener las comisiones BH asignadas
        comisionesBH_ids_asignadas = Asignacion.objects.values_list('comision_bh', flat=True)
        comisionesBH_no_asignadas = ComisionesBH.exclude(id__in=comisionesBH_ids_asignadas)
        #comisiones_no_asignadas
        comisiones_ids_sin_asignar = comisionesBH_no_asignadas.values_list('comision_id', flat=True)
        comisiones_sin_asignar = Comision.objects.all().filter(nombre__in = comisiones_ids_sin_asignar)


        aulas = Espacio_Aula.objects.all()  #Obtenemos todos lo espacios aulas
        #comisiones_con_herramientas = comisiones_sin_asignar.preferencias.through.
        #comisiones_ids_con_herramientas = Comision.preferencias.through.objects.all().filter(comision_id__in = comisiones_ids_sin_asignar)
        comisiones_ids_con_herramientas_rep = list(Comision.preferencias.through.objects.all().values_list('comision_id', flat=True))
        comisiones_ids_con_herramientas = []

        #Este bucle es para eliminar los ids reetidos de la lista de comisiones con preferencias de herramientas
        for ids_com_rep in comisiones_ids_con_herramientas_rep:
            if (not(ids_com_rep in comisiones_ids_con_herramientas)):
                comisiones_ids_con_herramientas.append(ids_com_rep)

        #comisiones_con_herramientas = Comision.preferencias.through.objects.all().filter(comision_id__in = comisiones_ids_con_herramientas)
        comisiones_con_herramientas = comisiones_sin_asignar.filter(id__in = comisiones_ids_con_herramientas)
        print(comisiones_ids_con_herramientas)
        print(comisiones_con_herramientas)



        #Aulas con Herramientas
        aulas_ids_con_herramientas_rep = list(Aula.herramientas.through.objects.all().values_list('aula_id', flat=True))
        aulas_ids_con_herramientas = []

        #Bucle para eliminar los ids repetidos de las aulas con herramientas
        for ids_aulas_rep in aulas_ids_con_herramientas_rep:
            if (not(ids_aulas_rep in aulas_ids_con_herramientas)):
                aulas_ids_con_herramientas.append(ids_aulas_rep)    #Se obtiene una lista con todos los ids de las aulas que tienen al menos una herramienta

        #comisiones_con_herramientas = Comision.preferencias.through.objects.all().filter(comision_id__in = comisiones_ids_con_herramientas)
        aulas_con_herramientas = aulas.filter(id__in = aulas_ids_con_herramientas)    #Objeto de aulas con al menos una herramienta
        print(aulas_ids_con_herramientas)
        print(aulas_con_herramientas)

        #aula_herr = {'id_aula':int, 'herramientas':[]}
        aulas_herrmientas = []    #Vamos a guardar todas las aulas que tienen herramientas con sus herramientas

        for au in aulas_ids_con_herramientas:
            herramientas = Aula.herramientas.through.objects.filter(aula_id = au).values_list('herramienta_id', flat=True)
            aula_herr = {'id_aula':au, 'herramientas':herramientas}
            aulas_herrmientas.append(aula_herr)     
            #print(herramientas)
            print(aula_herr)

        print(aulas_herrmientas)




        list_names_coms = [str]
        for com in comisiones_con_herramientas:
            list_names_coms.append(com.nombre)
        comisiones_BH_pref_herr = comisionesBH_no_asignadas.filter(comision_id__in = list_names_coms)    #Obtenemos las BH de las comisiones con preferencias de aulas


        #print(comisiones_BH_pref_aula)
        cant_herr_asig = 0
        cant_no_herr_asig = 0
        cant_total_herr_asig = comisiones_BH_pref_herr.count()

        

        print("Total de comisionesBH con Preferencias de Herramientas: {0}".format(cant_total_herr_asig))
        
        for comBH_pref_herr in comisiones_BH_pref_herr:
            comision = comisiones_con_herramientas.get(nombre = comBH_pref_herr.comision_id)
            #aula_pref = Espacio_Aula.objects.get(id = 1)
            cant_insc = comision.cant_insc

            

            herramientas_comision = Comision.preferencias.through.objects.filter(comision_id=comision.id).values_list('herramienta_id', flat=True)    #-><QuerySet []
            #herr_aula = Aula.herramientas.through.objects.filter(aula_id=comision.id).values_list('herramienta_id', flat=True)
            #definimos los atributos para filtrar los rangos de las asignaciones
            #print("herr_com")
            print("Herramientas Comision:")
            print(herramientas_comision)

            ids_aulas_matcheadas = []
            #MATCH entre aulas con herramientas y comisiones con requerimiento de aulas con herramientas
            for au_herr in aulas_herrmientas:
                herramientas = dict(au_herr)['herramientas']   #Obtengo las herrmientas de las aulas con herramientas -> <QuerySet [herramienta_id]>
                matches = all( elemento in herramientas for elemento in  herramientas_comision ) #Obtengo True si la lista de herranmientas de la comisión pertenece a la lista de herramientas del aula
                #
                if matches == True :
                    #print("posibles aulas")
                    ids_aulas_matcheadas.append(au_herr["id_aula"])  #agrego el id del aula a la lista de aulas matcheadas
                #print("herramientas MATCH")
                #print(herramientas)
                #print(matches)
            
            print("Aulas Matcheadas:")
            print(ids_aulas_matcheadas)

            if ((len(ids_aulas_matcheadas)) > 0): 
                print("existe al menos un aula match")

                aulas_matcheadas = Aula.objects.filter(id__in=ids_aulas_matcheadas)
                esp_aulas_matcheadas = Espacio_Aula.objects.filter(aula_id__in = aulas_matcheadas)

                print(esp_aulas_matcheadas)
                dia = comBH_pref_herr.dia
                hora_ini = comBH_pref_herr.hora_ini
                hora_fin = comBH_pref_herr.hora_fin
                

                asignaciones_en_rango = Asignacion.objects.filter(
                    comision_bh_id__dia=dia,
                    comision_bh_id__hora_ini__lt=hora_fin,
                    comision_bh_id__hora_fin__gt=hora_ini,
                )

                # Excluir las aulas que están asignadas en ese rango de horario, para obtener las aulas disponibles en el rango requerido
                aulas_disponibles_BH = esp_aulas_matcheadas.exclude(asignacion__in=asignaciones_en_rango)
                
                #Se agrega la ponderación de hasta 10 inscritos más que la capacidad másxima del AULA
                if cant_insc <= 10:
                    cant_insc = 0
                else:
                    cant_insc = cant_insc - 10

                #FIiltro por aulas con mayor o igual capacidad que la requerida por la comision
                aulas_disponibles_BH = aulas_disponibles_BH.filter(
                    capacidad_total__gt = cant_insc
                ).order_by("capacidad_total")

                


                #De todas las aulas con la capacidad y herramientas necesarias que no han sido asignadas, vamos a asignar la 1era
                if aulas_disponibles_BH.count() > 0:
                    aula_pref_herr1 = aulas_disponibles_BH.first()
                    print("AUla PREF HERR")
                    print(aula_pref_herr1)
                    print("Aula: "+ aula_pref_herr1.nombre_combinado + " DISPONIBLE!!")
                    print("Comision BH: "+ comBH_pref_herr.__str__())
                    #Asignacion.objects.create(espacio_aula=aula_pref_herr1, comision_bh=comBH_pref_herr)
                    Asignacion.objects.create(espacio_aula=aula_pref_herr1, comision_bh=comBH_pref_herr, real=True)
                    ################################### Verificación de las aulas extensibles ########################
                    ###acá hay que corregir
                    #Au_Rep_Ids = {"id": ids_esp_aula_ext,"nombre_combinado": nombre, "repeticiones": num_repeticiones, "ids_aulas":ids_aulas_ext}
                    #aul_rep_ids_list.append(Au_Rep_Ids)
                    asignacion_final = []
                    for aurl in aul_rep_ids_list:
                        #print("dict:", aurl)
                        ### verificamos desde el lado de las aulas extensibles con más de una
                        if (aula_pref_herr1.id in aurl["id"]):
                            for aula_pref_herr1.id in aurl["ids_aulas"]:
                                asignacion_final.append(aurl["id"] + aurl["ids_aulas"])
                        
                        

                        ### verificamos desde el lado de las aulas individuales que se pueden hacer extensibles
                        else: #
                            if(aula_pref_herr1.id in aurl["ids_aulas"]):
                                asignacion_final.append(aurl["id"])
                            
                        
                            #Asignacion.create
                        #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                        #for asig in asignacion_final:
                         #   aula_asig = Espacio_Aula.objects.get(id = asig)
                          #  Asignacion.objects.create(espacio_aula=aula_asig, comision_bh=comiBH)
                    #simplificamos la lista para no tener ids repetidos
                    asig_final_simple = []
                    for asig_f in asignacion_final:
                        for asf in asig_f:
                            if not(asf in asig_final_simple):
                                asig_final_simple.append(asf)
                    #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                    for asig in asig_final_simple:
                        aula_pref_herr1 = Espacio_Aula.objects.get(id = asig)
                        Asignacion.objects.create(espacio_aula=aula_pref_herr1, comision_bh=comBH_pref_herr, real=False)    
                    print("###################_____________LISTAS-ASIGNACION FINAL:", asignacion_final)
                    #print("asig_final_final", asig_final_final)
                    print("asig_final_simple", asig_final_simple)
                    print("Asignación Realizada con Éxito")
                    cant_herr_asig +=1
                    cant_tot_asig_algoritmo +=1
                    #FALTA AGREGAR LA VERIFICACIÓN Y ASIGNACIÓN DE LAS AULAS EXTENSIBLES
                    ######################################################################### verificacion de las aulas extensibles
                else:
                    print("No EXISTEN AULAS DISPONIBLES!!")
                    print("Comision BH: "+ comBH_pref_herr.__str__())
                    print("NO SE PUDO REALIZAR LA ASIGNACIÓN!!")
                    cant_no_herr_asig +=1
                    cant_tot_no_asig_algoritmo +=1

            
            else:
                print("NO EXISTE ningun aula MATCH")
                print("NO SE PUDO REALIZAR LA ASIGNACIÓN!!")

            print("{0} Comisiones Asignadas a las Aulas con Herramientas Requeridas!!".format(cant_herr_asig))
            print("{0} Comisiones NO ASIGNADAS a las Aulas con Herramientas Requeridas!!".format(cant_no_herr_asig))
            



        #### FIN DE ASIGNACION DE COMISIONES CON HERRAMIENTAS ####

        #### ASIGNACIÓN DE COMISIONES POR CANTIDAD DE INSCRITOS ####
        #Obtener las comisiones BH asignadas
        comisionesBH_ids_asignadas = Asignacion.objects.values_list('comision_bh', flat=True)
        comisionesBH_no_asignadas = ComisionesBH.exclude(id__in=comisionesBH_ids_asignadas).order_by("-comision_id__cant_insc")
        #comisiones_no_asignadas
        comisiones_ids_sin_asignar = comisionesBH_no_asignadas.values_list('comision_id', flat=True)
        comisiones_sin_asignar = Comision.objects.all().filter(nombre__in = comisiones_ids_sin_asignar)


        cant_asig = 0
        cant_not_asig = 0
        cantidad_total_asig = comisionesBH_no_asignadas.count()


        aulas = Espacio_Aula.objects.all()  #Obtenemos todos lo espacios aulas

        print("Total de comisionesBH para asignar: {0}".format(cantidad_total_asig))
       

        for comiBH in comisionesBH_no_asignadas:
            comision = Comision.objects.get(nombre = comiBH.comision_id)
            cant_insc = comision.cant_insc
            #aula_pref = Espacio_Aula.objects.get(id = comision.aula_exclusiva_id)
            #definimos los atributos para filtrar los rangos de las asignaciones

            if (cant_insc > 0):
                dia = comiBH.dia
                hora_ini = comiBH.hora_ini
                hora_fin = comiBH.hora_fin
                

                asignaciones_en_rango = Asignacion.objects.filter(
                    comision_bh_id__dia=dia,
                    comision_bh_id__hora_ini__lt=hora_fin,
                    comision_bh_id__hora_fin__gt=hora_ini,
                )

                # Excluir las aulas que están asignadas en ese rango de horario, para obtener las aulas disponibles en el rango requerido
                aulas_disponibles_BH = aulas.exclude(asignacion__in=asignaciones_en_rango)

                

                print("Aulas disponibles antes de aplicar el filtro", aulas_disponibles_BH)

                for au_ext in aulas_disponibles_BH:
                    if (au_ext.id in ids_esp_aula_ext ):
                        print("De las aulas disponibles para una comision con herramienta, se debe verificar si el aula extensible realmente está disponible")
                        
                        #for aril in aul_rep_ids_list:
                        #Se va a buscar el aula en la lista de aulas extensibles y retornar la posicion del elemento
                        ind = -1
                        for index, diccionario in enumerate(aul_rep_ids_list):
                            if au_ext.nombre_combinado in diccionario.values():
                                print(f"El valor '{au_ext.nombre_combinado}' se encuentra en el diccionario en la posición {index}")
                                ind = index
                                break  # Para detener la búsqueda luego de encontrar la primera coincidencia
                            else:
                                print(f"El valor '{au_ext.nombre_combinado}' no se encuentra en ninguno de los diccionarios")

                        if ind > -1:
                            aux_ver = aul_rep_ids_list[ind]["nombre_combinado"]
                            list_aulas_ids = aul_rep_ids_list[ind]["ids_aulas"]
                            print("aula_nombre_combinado:", aux_ver)
                            print("lista de aulas relacionadas: ", list_aulas_ids)

                            ids_au_ext_nd = []
                            aulas_matcheadas = []
                            for id_aula in list_aulas_ids:
                                aula = Espacio_Aula.objects.get(id = id_aula)

                                #FALTA CORREGIR ESTA PARTE
                                if (aulas_disponibles_BH.contains(aula)):
                                    print(f"aula {aula.nombre_combinado} perteneciente a {aux_ver} Disponible en la BH requerida por la comision")
                                else: 
                                    print(f"aula {aula.nombre_combinado} NO DISPONIBLE")
                                    ids_au_ext_nd.append(aula.id)
                                    
                                    #MATCH entre aulas con herramientas y comisiones con requerimiento de aulas con herramientas
                                    for au_ext in aul_rep_ids_list:
                                        if aula.id in au_ext["ids_aulas"]:
                                            if not(au_ext in aulas_matcheadas):
                                                aulas_matcheadas.append(au_ext)
                            print("aulas matcheadas", aulas_matcheadas)

                            list_names_aulas_matcheadas = []
                            for aulasM in aulas_matcheadas:
                                list_names_aulas_matcheadas.append(aulasM["nombre_combinado"])

                            print("nombres de las aulas matcheadas: ", list_names_aulas_matcheadas)

                            aulas_disponibles_BH = aulas_disponibles_BH.exclude(nombre_combinado__in = list_names_aulas_matcheadas)
                                        
                            #print("aulas extensibles no disponibles: ", ids_au_ext_nd)
                            #ids_aulas_ext_matcheadas = []
                            
                                #print(ids_aulas_matcheadas)

                #Se agrega la ponderación de hasta 10 inscritos más que la capacidad másxima del AULA
                if cant_insc <= 10:
                    cant_insc = 0
                else:
                    cant_insc = cant_insc - 10
                
                #FIiltro por aulas con mayor capacidad
                aulas_disponibles_BH = aulas_disponibles_BH.filter(
                    capacidad_total__gt = cant_insc
                ).order_by("capacidad_total")

                print("Aulas Disponibles", aulas_disponibles_BH)
                if aulas_disponibles_BH.count() > 0:
                    aula_asig = aulas_disponibles_BH.first()
                    print("Aula: "+ aula_asig.nombre_combinado + " DISPONIBLE!!")
                    print("Comision BH: "+ comiBH.__str__())

                    Asignacion.objects.create(espacio_aula=aula_asig, comision_bh=comiBH, real=True)
                    ################################### Verificación de las aulas extensibles ########################
                    ###acá hay que corregir
                    #Au_Rep_Ids = {"id": ids_esp_aula_ext,"nombre_combinado": nombre, "repeticiones": num_repeticiones, "ids_aulas":ids_aulas_ext}
                    #aul_rep_ids_list.append(Au_Rep_Ids)
                    asignacion_final = []
                    for aurl in aul_rep_ids_list:
                        #print("dict:", aurl)
                        ### verificamos desde el lado de las aulas extensibles con más de una
                        if (aula_asig.id in aurl["id"]):
                            for aula_asig.id in aurl["ids_aulas"]:
                                asignacion_final.append(aurl["id"] + aurl["ids_aulas"])
                        
                        

                        ### verificamos desde el lado de las aulas individuales que se pueden hacer extensibles
                        else: #
                            if(aula_asig.id in aurl["ids_aulas"]):
                                asignacion_final.append(aurl["id"])
                            
                        
                            #Asignacion.create
                        #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                        #for asig in asignacion_final:
                         #   aula_asig = Espacio_Aula.objects.get(id = asig)
                          #  Asignacion.objects.create(espacio_aula=aula_asig, comision_bh=comiBH)
                    #simplificamos la lista para no tener ids repetidos
                    asig_final_simple = []
                    for asig_f in asignacion_final:
                        for asf in asig_f:
                            if not(asf in asig_final_simple):
                                asig_final_simple.append(asf)
                    #creamos las asignaciones a todas las aulas para que ya no esté disponible esa BH
                    for asig in asig_final_simple:
                        aula_asig = Espacio_Aula.objects.get(id = asig)
                        Asignacion.objects.create(espacio_aula=aula_asig, comision_bh=comiBH, real=False)    
                    print("###################_____________LISTAS-ASIGNACION FINAL:", asignacion_final)
                    #print("asig_final_final", asig_final_final)
                    print("asig_final_simple", asig_final_simple)
                    print("Asignación Realizada con Éxito")
                    cant_asig +=1
                    cant_tot_asig_algoritmo +=1
                    #FALTA AGREGAR LA VERIFICACIÓN Y ASIGNACIÓN DE LAS AULAS EXTENSIBLES
                    ######################################################################### verificacion de las aulas extensibles
                else:
                    print("Aula: no disponible!!!")
                    print("Comision BH: "+ comiBH.__str__())
                    print("NO SE PUDO REALIZAR LA ASIGNACIÓN!!")
                    cant_not_asig +=1
                    cant_tot_no_asig_algoritmo +=1
            else:
                print("Comision BH: "+ comiBH.__str__())
                cant_not_asig +=1
                cant_tot_no_asig_algoritmo +=1









        

        
        print("{0} Comisiones Asignadas por Cantidad Inscritos!!".format(cant_asig))
        print("{0} Comisiones NO ASIGNADAS por cantidad Inscritos!!".format(cant_not_asig))

        cantidad_total_asignaciones = Asignacion.objects.all().count()
        cantidad_total_pendientes = ComisionesBH.count() - cantidad_total_asignaciones


        print("{0} Comisiones Asignadas en TOTAL!!".format(cantidad_total_asignaciones))
        print("{0} Comisiones NO ASIGNADAS del TOTAL!!".format(cantidad_total_pendientes))

        context["comisiones_asignadas_algoritmo"] = cant_tot_asig_algoritmo
        context["comisiones_no_asignadas_algoritmo"] = cant_tot_no_asig_algoritmo
        context["total_algoritmo"] = cant_tot_asig_algoritmo + cant_tot_no_asig_algoritmo

        context["comisiones_asignadas"] = cantidad_total_asignaciones
        context["comisiones_no_asignadas"] = cantidad_total_pendientes
        context["total_comisiones"] = cantidad_total_asignaciones + cantidad_total_pendientes

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