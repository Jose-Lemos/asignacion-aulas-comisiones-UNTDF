from django.views.generic import ListView
from app.models import Asignacion, Comision_BH
from django.db.models import Q

class ComisionesSinAsignarView(ListView):
    model = Comision_BH
    template_name = "comisiones_sin_asignar.html"
    context_object_name = "comisiones"
    paginate_by = 30

    def get_queryset(self):
        txt_buscador = self.request.GET.get("buscador")

        if txt_buscador:
            ComisionesBH = Comision_BH.objects.filter(
                Q(comision__nombre__icontains = txt_buscador)|
                Q(comision__materia__nombre__icontains = txt_buscador)
                )
        else:
            ComisionesBH = Comision_BH.objects.all().order_by("comision")

            #Obtener las comisiones asignadas
            comisionesBH_asignadas = Asignacion.objects.values_list('comision_bh', flat=True)
            comisiones_no_asignadas = ComisionesBH.exclude(id__in=comisionesBH_asignadas)
            ComisionesBH = comisiones_no_asignadas

        return ComisionesBH