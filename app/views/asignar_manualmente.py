from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from ..forms import AsignacionManualForm
from ..models import *
from django.db.models import F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.utils import timezone

class AsignarManualmenteView(TemplateView):
    template_name = 'asignacion_manual.html'
    alert = None

    from django.db.models import F
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comisiones_no_asignadas = Comision_BH.objects.exclude(asignacion__isnull=False)
        context['comisiones'] = comisiones_no_asignadas
        # Obtener todas las aulas
        aulas = Aula.objects.all()

       
        context['aulas'] = aulas  # Añadir aulas al contexto

        return context
@require_POST
def asignar_aula(request):
    if request.method == 'POST':
        comision_bh_id = request.POST.get('comision_bh')
        aula_id = request.POST.get('aula')

        if comision_bh_id and aula_id:
            comision_bh = Comision_BH.objects.get(pk=comision_bh_id)
            aula = Aula.objects.get(pk=aula_id)

            # Verifica si el aula está disponible en el día y horario de la comisión
            asignaciones_en_aula = Asignacion.objects.filter(
                aula=aula,
                comision_bh__dia=comision_bh.dia,
                comision_bh__hora_ini__lte=comision_bh.hora_ini,
                comision_bh__hora_fin__gte=comision_bh.hora_fin
            )

            if not asignaciones_en_aula:
                Asignacion.objects.create(aula=aula, comision_bh=comision_bh)
                return HttpResponse('Aula asignada con éxito.')
            else:
                return HttpResponse('El aula no está disponible en ese horario.')
    
    return HttpResponse('No se pudo asignar el aula.')