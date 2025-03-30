from typing import Any
from django.views.generic import TemplateView
from app.models import Asignacion, Aula, Comision_BH, Espacio_Aula



class aulas_asignadas_reporte(TemplateView):
    template_name = "aulas_asignadas_reporte.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")

        try:
            esp_aula = Espacio_Aula.objects.get(id=pk)
            context["esp_aula"] = esp_aula
        except Espacio_Aula.DoesNotExist:
            context["error"] = "Espacio de aula no encontrado"
            return context

        # Si es un grupo de aulas extensibles, obtiene todas las aulas asociadas
        aulas = esp_aula.aulas.all() if esp_aula.aulas.exists() else [esp_aula]
        context["aulas"] = aulas

        # Obtener asignaciones de este espacio
        asignaciones = Asignacion.objects.filter(espacio_aula=esp_aula)
        context["asignaciones"] = asignaciones

        # Obtener las comisiones relacionadas con las asignaciones
        comisionesBH_ids = asignaciones.values_list("comision_bh_id", flat=True)
        comisionBH_QS = Comision_BH.objects.filter(id__in=comisionesBH_ids)
        context["ComisionesBH"] = comisionBH_QS

        return context


