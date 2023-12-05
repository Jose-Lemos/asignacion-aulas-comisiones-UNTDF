from django.db.models import Q, F, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.shortcuts import render
from requests import request
from django.views.generic import TemplateView
from app.models import Asignacion, Comision, Comision_BH, Espacio_Aula


class AsignarAutomaticamenteView(TemplateView):
    template_name = 'aula_disponible.html'

def obtener_aula_disponible():
    hora_a_verificar = '09:00:00'  # Puedes ajustar la hora aquí
    capacidad_requerida = 5  # Puedes ajustar la capacidad requerida aquí
    aula_exclusiva_id = 10  # Puedes ajustar el ID del aula exclusiva aquí

    subquery_1 = Espacio_Aula.objects.filter(
        id__in=Asignacion.objects.filter(
            ##comision_bh__hora_ini__lte >=hora_a_verificar,
            #comision_bh__hora_fin__gte=hora_a_verificar
        ).values('espacio_aula')
    )

    subquery_2 = Espacio_Aula.objects.annotate(
        capacidad_total=Coalesce(F('aula__capacidad_total'), 0)
    ).filter(
        capacidad_total__gte=capacidad_requerida
    ).order_by('capacidad_total').values('id')[:1]

    subquery_3 = Espacio_Aula.objects.filter(aula__id=aula_exclusiva_id).values('id')

    aula_disponible = Espacio_Aula.objects.exclude(
        id__in=subquery_1
    ).filter(
        Q(id__in=subquery_2) | Q(id__in=subquery_3)
    ).first()

    aula_disponible = obtener_aula_disponible()  # Llama a la función para obtener el aula disponible

    context = {
        'aula_disponible': aula_disponible
    }

    return render (request, 'aula_disponible.html', context)



def asignar_aulas():
    # Obtener todas las comisiones
    comisiones = Comision.objects.all()

    for comision in comisiones:
        herramientas_preferidas = comision.preferencias.all()

        aula_disponible = Espacio_Aula.objects.filter(
            capacidad_total__gte=comision.cant_insc,
            aula__herramientas__in=herramientas_preferidas
        ).first()

        if aula_disponible:
            # Obtener todas las Comision_BH asociadas a la Comision actual
            comisiones_bh = Comision_BH.objects.filter(comision=comision)

            # Intentar asignar el aula a cada Comision_BH encontrado
            for comision_bh in comisiones_bh:
                try:
                    asignacion = Asignacion.objects.create(
                        espacio_aula=aula_disponible,
                        comision_bh=comision_bh
                    )
                    print(f"Asignación creada: {asignacion}")
                except:
                    print(f"No se pudo crear la asignación para la comisión: {comision}")
        else:
            print(f"No se encontró un aula disponible para la comisión: {comision}")


# Llamar a la función para realizar las asignaciones
asignar_aulas()