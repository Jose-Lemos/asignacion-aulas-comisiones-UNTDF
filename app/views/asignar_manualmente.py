from ..models import *
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect


# class ConfirmarAsignacionView(TemplateView):
#     template_name = 'confirmar_asignacion.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Obtén la asignación actual que se va a eliminar y la nueva que se propone
#         asignacion_actual = kwargs.get('asignacion_actual')
#         nueva_asignacion = kwargs.get('nueva_asignacion')

#         context['asignacion_actual'] = asignacion_actual
#         context['nueva_asignacion'] = nueva_asignacion
#         return context

#     def post(self, request, *args, **kwargs):
#         if 'confirmar' in request.POST:
#             # Aquí eliminas la asignación previa y realizas la nueva
#             asignacion_actual = kwargs.get('asignacion_actual')
#             nueva_asignacion = kwargs.get('nueva_asignacion')

#             # Lógica para eliminar la asignación previa y realizar la nueva
#             asignacion_actual.delete()
#             nueva_asignacion.save()

#             messages.success(request, "La nueva asignación se realizó con éxito.")
#             return redirect('asignar-manual-aula')  # Redirige a una página de éxito
#         else:
#             messages.error(request, "La asignación no fue confirmada.")
#             return redirect('asignar-manual-aula')  # Redirige a una página de cancelación

class AsignarManualmenteView(TemplateView):
    template_name = 'asignacion_manual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comisiones_no_asignadas = Comision_BH.objects.exclude(asignacion__isnull=False)
        context['comisiones'] = comisiones_no_asignadas
        # Obtener todas las aulas
        aulas = Espacio_Aula.objects.all()
        print(aulas)
       
        context['aulas'] = aulas  # Añadir aulas al contexto
        context["mensaje"] = ""

        print("context:", context)



        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            comision_bh_id = request.POST.get('comision_bh')
            espacio_aula_id = request.POST.get('aula')
            context = super().get_context_data(**kwargs)
            print("comisionBH:"+comision_bh_id)
            print("esp_aula:"+espacio_aula_id)

            if comision_bh_id and espacio_aula_id:
                comision_bh = Comision_BH.objects.get(pk=comision_bh_id)
                espacio_aula = Espacio_Aula.objects.get(pk=espacio_aula_id)

                # Verifica si el aula está disponible en el día y horario de la comisión
                asignaciones_en_aula = Asignacion.objects.filter(
                    espacio_aula=espacio_aula,
                    comision_bh__dia=comision_bh.dia,
                    comision_bh__hora_ini__lte=comision_bh.hora_ini,
                    comision_bh__hora_fin__gte=comision_bh.hora_fin
                )


                if not asignaciones_en_aula:
                    Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh)
                    context["mensaje"] = "Asignación Realizada con Éxito"
                    context["asig_OK"] = False
                    #messages.success(request, "La nueva asignación se realizó con éxito.")
                    #return self.render_to_response(context)  # Redirige a una página de éxito
                else:
                    context['asignacion_actual'] = asignaciones_en_aula
                    context['comision_bh'] = comision_bh
                    context['espacio_aula'] = espacio_aula
                    context["mensaje"] = "El aula no está disponible en ese horario"
                    context["asig_OK"] = True
                    #messages.error(request, "La asignación no fue confirmada.")
                    #return redirect('confirmar-asignacion')  # Redirige a una página de cancelación
            print("context:", context)
            for asig in asignaciones_en_aula:
                print("asig_com:", asig.comision_bh)
                print("asig_aula:", asig.espacio_aula)
                print("dia:", asig.comision_bh.dia)
        
        return self.render_to_response(context)


class AsignarManualmenteViewComision(ListView):
    model = Comision_BH
    template_name = 'asignacion_manual_comision_bh.html'
    context_object_name = "comisiones"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parametro = self.kwargs.get('comi')
        # Hacer algo con el parámetro obtenido
        context['parametro'] = parametro  # Agregar el parámetro al contexto si deseas utilizarlo en el template
        context['comi_sel'] = Comision_BH.objects.get(id=parametro)
        
        return context
    

class AsignarManualmenteAula(TemplateView):
    template_name = 'asignar_aula_manual.html'
    context_object_name = "aulas"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parametro = self.kwargs.get('comBH')
        #print(parametro)
        # Hacer algo con el parámetro obtenido
        #context['parametro'] = parametro  # Agregar el parámetro al contexto si deseas utilizarlo en el template
        context['comisionBH'] = Comision_BH.objects.get(id=parametro)

        comision_BH = Comision_BH.objects.get(id=parametro)
        hora_ini = comision_BH.hora_ini
        hora_fin = comision_BH.hora_fin
        dia = comision_BH.dia

        comision = Comision.objects.get(nombre= comision_BH.comision_id)
        #materia = comision.materia
        cant_insc = comision.cant_insc
        print(comision)

        print(dia, hora_ini, hora_fin)
        #asignaciones = Asignacion.objects.filter(espacio_aula_id__ = 1)
        aulas = Espacio_Aula.objects.all()

        # Filtrar las asignaciones que están dentro del rango de horario
        asignaciones_en_rango = Asignacion.objects.filter(
            comision_bh_id__dia=dia,
            comision_bh_id__hora_ini__lt=hora_fin,
            comision_bh_id__hora_fin__gt=hora_ini,
         )

        # Excluir las aulas que están asignadas en ese rango de horario
        aulas_no_asignadas_rango = aulas.exclude(asignacion__in=asignaciones_en_rango)

        #FIiltro por aulas con mayor capacidad
        # Obtener todas las aulas
        aulas_no_asignadas_rango = [
            aula for aula in aulas
            if aula.capacidad_total_calculada() > (cant_insc - 11)
        ]

        # Ordenar por capacidad calculada
        aulas_no_asignadas_rango.sort(key=lambda a: a.capacidad_total_calculada())
        # Aulas disponibles que no están asignadas en el rango de horario
        # Aulas con la capacidad suficiente
        print(aulas_no_asignadas_rango)
    
        context["aulas_disponibles"] = aulas_no_asignadas_rango

        #print(context)
        return context
    
    def post(self, request, **kwargs):
        if request.method == 'POST':
            comision_bh_id = request.POST.get('comision_bh')
            espacio_aula_id = request.POST.get('aula')
            context = super().get_context_data(**kwargs)
            print("comisionBH:"+comision_bh_id)
            print("esp_aula:"+espacio_aula_id)

            

            if comision_bh_id and espacio_aula_id:
                comision_bh = Comision_BH.objects.get(pk=comision_bh_id)
                espacio_aula = Espacio_Aula.objects.get(pk=espacio_aula_id)

                # Verifica si el aula está disponible en el día y horario de la comisión
                asignaciones_en_aula = Asignacion.objects.filter(
                    espacio_aula=espacio_aula,
                    comision_bh__dia=comision_bh.dia,
                    comision_bh__hora_ini__lte=comision_bh.hora_ini,
                    comision_bh__hora_fin__gte=comision_bh.hora_fin
                )

                if not asignaciones_en_aula:
                    Asignacion.objects.create(espacio_aula=espacio_aula, comision_bh=comision_bh)
                    context["mensaje"] = "Asignación Realizada con Éxito"
                else:
                    context['asignacion_actual'] = asignaciones_en_aula
                    context['comision_bh'] = comision_bh
                    context['espacio_aula'] = espacio_aula
                    context["mensaje"] = "El aula no está disponible en ese horario"
        
        return self.render_to_response(context)

        
    

