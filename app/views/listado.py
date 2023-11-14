from django.views.generic import TemplateView
from app.models import Comision, Asignacion, Aula

class ComisionesSinAsignarView(TemplateView):
    template_name = 'comisiones_sin_asignar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las comisiones
        comisiones = Comision.objects.all()
        # Obtener las comisiones asignadas
        comisiones_asignadas = Asignacion.objects.values_list('comision_bh__comision', flat=True)
        # Filtrar las comisiones que no han sido asignadas
        comisiones_no_asignadas = comisiones.exclude(nombre__in=comisiones_asignadas)
        context['comisiones'] = comisiones_no_asignadas


        ###
        for p in Aula.objects.raw("""
                                  select *
                                  from App_Aula
                                  
                                  """): print({})
        ###


        return context