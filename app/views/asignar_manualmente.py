from ..models import *
from django.views.generic import TemplateView, ListView


class AsignarManualmenteView(TemplateView):
    template_name = 'asignacion_manual.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comisiones_no_asignadas = Comision_BH.objects.exclude(asignacion__isnull=False)
        context['comisiones'] = comisiones_no_asignadas
        # Obtener aulas libres en la hora que necesite la comision seleccionada 
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
            print(comision_bh_id)
            print(espacio_aula_id)

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
    

class AsignarManualmenteViewComisionAula(ListView):
    model = Aula
    template_name = 'asignacion_manual_asignar.html'
    context_object_name = "aulas"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        parametro = self.kwargs.get('aula')
        # Hacer algo con el parámetro obtenido
        context['parametro'] = parametro  # Agregar el parámetro al contexto si deseas utilizarlo en el template
        context['aula_sel'] = Espacio_Aula.objects.get(id=parametro)

        return context