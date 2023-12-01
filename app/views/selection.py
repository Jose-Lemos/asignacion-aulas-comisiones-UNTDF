from django.views.generic import ListView
from app.models import Espacio_Aula, Comision_BH, Asignacion
from django.db.models import Q


class select_aula(ListView):
    model = Espacio_Aula
    template_name = "seleccionar_aula.html"
    context_object_name = "aulas"
    paginate_by = 30

    def get_queryset(self):
        txt_buscador = self.request.GET.get("buscador")

        if txt_buscador:
            Aulas = Espacio_Aula.objects.filter(
                Q(aula__nombre__icontains = txt_buscador)
                )
        else:
            Aulas = Espacio_Aula.objects.all().order_by("aula")

        return Aulas
    
class selection_comision_BH(ListView):
    model = Comision_BH
    template_name = "seleccionar_comision_BH.html"
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