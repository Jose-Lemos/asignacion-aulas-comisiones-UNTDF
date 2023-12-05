from ..models import *
from django.views.generic import TemplateView, ListView
from django.db.models import Q


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
                    context["mensaje"] = "El aula no está disponible en ese horario"
        
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
            comision_bh_id__hora_fin__gt=hora_ini,
        )

        # Excluir las aulas que están asignadas en ese rango de horario
        aulas_no_asignadas_rango = aulas.exclude(asignacion__in=asignaciones_en_rango)

        #FIiltro por aulas con mayor capacidad
        aulas_no_asignadas_rango = aulas_no_asignadas_rango.filter(
            capacidad_total__gt = cant_insc
        ).order_by("capacidad_total")

        
        # Aulas disponibles que no están asignadas en el rango de horario
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
                    context["mensaje"] = "El aula no está disponible en ese horario"
        
        return self.render_to_response(context)

        
    

