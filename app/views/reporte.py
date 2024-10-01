from typing import Any
from django.views.generic import TemplateView
from app.models import Asignacion, Aula, Comision_BH, Espacio_Aula



class aulas_asignadas_reporte(TemplateView):
    template_name = "aulas_asignadas_reporte.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get("pk")
        print(pk)

        
        esp_aula = Espacio_Aula.objects.get(id=pk)
        context["esp_aula"] = esp_aula

        aula = Aula.objects.get(id=esp_aula.aula_id)
        context["aula"] = aula

        
        asignaciones = Asignacion.objects.filter(espacio_aula_id = pk, real=True)
        context["asignaciones"] = asignaciones

        asig_list = list(asignaciones)
        comisionesBH_ids = []
        for asig in asig_list:
            comiBH = Comision_BH.objects.get(id=asig.comision_bh_id)
            comisionesBH_ids.append(comiBH.id)


        comisionBH_QS = Comision_BH.objects.filter(id__in = comisionesBH_ids)
        context["ComisionesBH"] = comisionBH_QS

        print(context)

        return context
    

