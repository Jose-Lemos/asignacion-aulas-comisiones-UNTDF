"""from django.contrib import admin
from django.db.models import QuerySet
from app.models import Herramienta, Aula, Carrera, Materia, Comision, Comision_BH, Asignacion

#update titles
admin.site.site_header = 'Asignación de Aulas'
admin.site.index_title = 'Panel de Administración'
admin.site.site_title = 'Asignación de Aulas'

# Register your models here.
admin.site.register(Herramienta)
admin.site.register(Aula)
admin.site.register(Carrera)
admin.site.register(Materia)
admin.site.register(Comision)
admin.site.register(Asignacion)
#admin.site.register(Comision_BH)


#Filtro para las comisiones sin asignar y comisiones asignadas
class filtro_comsiones_sin_asignar(admin.SimpleListFilter):
    title = 'Filtros'  # El nombre que se mostrará en el admin
    parameter_name = 'id'  # El nombre del parámetro GET en la URL

    def lookups(self, request, model_admin):
        # Define los valores que se mostrarán como opciones de filtro
        return (
            ('CSA', 'Comisiones sin Asignar'),
            ('CA', 'Comisiones Asignadas'),
            # Agregar más opciones si es necesario
        )

    def queryset(self, request, queryset):
        asignaciones = Asignacion.objects.all()
        #comisiones_bh = Comision_BH.objects.all()
        comisiones_asig = []

        for qy in queryset:
         #   ids.append(id)
            print(qy.id)

        if asignaciones.exists() == True:
            print("Existe al menos una asignación realizada")
            for asig in asignaciones:
                print(asig.get_com())
                comisiones_asig.append(asig.get_com())
        else:
            print("No existen asignaciones realizadas")
        
        if self.value() == 'CSA':
                # Aplica el filtro correspondiente si se selecciona 'Opción CSA'
            print("Estamos en CSA")
            if asignaciones.exists() == False:    #Si no existen asignaciones realizadas, entonces retorna todas las comisiones_bh
                print("No existen asignación realizada")
                #return queryset.filter(id__in=asignaciones[0])
                return Comision_BH.objects.all()
            else:
                return queryset.exclude(id__in = comisiones_asig)     #Si existe al menos una asignación, entonces va a retornar todas las comisiones_bh que NO PERTENECEN a la lista de ids de las comisiones_bh ya asignadas
        if self.value() == 'CA':
                # Aplica el filtro correspondiente si se selecciona 'Opción CA'
            print("Estamos en CA")
            if asignaciones.exists() == True:
                print("Existe al menos una asignación realizada")
                #return queryset.filter(id__in=asignaciones[0])
                return queryset.filter(id__in = comisiones_asig)    #Si existe al menos una asignación, entonces retorna todas las comisiones_bh que ya fueron asignadas
            else:
                return queryset.none()    #Caso contrario, retorna un QuerySet vacío.




# Esta función recibe un queryset con los usuarios seleccionados y lanzaremos un update para desactivarlos
def asignar_aulas(modeladmin, request, queryset):
    for x in queryset:
        print(x.id, x.dia)
    #Acá debemos completar el algoritmo de asignación
    #queryset.update(is_active=False)

@admin.register(Comision_BH)
class Asignacion_Comision_Admin(admin.ModelAdmin):
    

    list_display = ('pk','dia', 'hora_ini', 'hora_fin', 'fecha_ini', 'fecha_fin', 'comision_id')
    list_display_links = ('pk', 'comision_id')
    list_filter = (filtro_comsiones_sin_asignar,)    #Agrega el filtro al listado del modelo

    # En actions añadimos las funcionalidades extra
    actions = [asignar_aulas]
"""