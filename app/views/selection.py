from django.views.generic import ListView
from app.models import Espacio_Aula
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