from django.db import models

class Herramienta(models.Model):
   # pk = models.AutoField(primary_key=True) # integer: autoincremental
   # proyector = models.BooleanField()
  #  polycom = models.BooleanField()
  #  televisor = models.BooleanField()
  #  computadoras = models.BooleanField()
    nombre = models.CharField(max_length=255)
    class Meta: # Los índices van a ayudar al momento de recorrer las asignaciones, cuando busquemos las aulas vacías para el periodo actual
        indexes = [
            models.Index(fields=['pk', 'proyector', 'polycom', 'televisor', 'computadoras']), # compuesto
        ]

class Aula(models.Model):
    pk = models.IntegerField(primary_key=True) # espacio o integer: nuestro, sin consumirlas, sino cargandolas nososotros
    nombre = models.CharField(max_length=255) # nombre o string: nuestro
    cant_cupos = models.IntegerField()
    aula_compartida = models.ForeignKey('self', on_delete=models.CASCADE, null=True) 

    class Meta:
        indexes = [
            models.Index(fields=['pk', 'nombre']), # compuesto
        ]

class Materia(models.Model):
    # Recordar hacer coincidir la PK de Materia con el id de Elemento en Guaraní
    pk = models.IntegerField(primary_key=True) # elemento
    nombre = models.CharField(max_length=255) # nombre
    codigo = models.CharField(max_length=20) # codigo
    carrera = models.CharField(max_length=255) # string: simplificamos datos, se puede obtener de sga_elementos_plan.plan_version.nombre

class Comision(models.Model):
    pk = models.IntegerField(primary_key=True) # comision
    nombre = models.CharField(max_length=100) # nombre
    cant_insc = models.IntegerField() # consulta sobre sga_insc_cursada. Tiene ser UPDATE cada nuevo consumo que se haga = sga_insc_cursada.comision JOIN (sga_comisiones_bh.asignacion.fecha_desde >= currentDate())
    # aula_preferida = models.ForeignKey(Aula, on_delete=models.CASCADE, null=True) # No sé si realmente es necesaria. Las predefinidas las podemos cargar a mano, y luego correr el algoritmo sobre estas. Para esto hay que tener en cuenta que el 
    comision_compartida = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

class Comision_BH(models.Model): # Misma lógica de consumo que para la cant_insc --> sga_insc_cursada.comision JOIN (sga_comisiones_bh.asignacion.fecha_desde >= currentDate())
    pk = models.AutoField(primary_key=True)
    comision = models.ForeignKey(Comision, on_delete=models.CASCADE, null=True)
    dia = models.CharField(max_length=9)
    hora_ini = models.TimeField()
    hora_fin = models.TimeField()
    fecha_ini = models.DateField()
    fecha_fin = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['pk', 'fecha_fin']), # compuesto
        ]

class Asignacion(models.Model):
    pk = models.AutoField(primary_key=True)
    aula =  models.ForeignKey(Aula, on_delete=models.CASCADE, null=True)
    comision_bh =  models.ForeignKey(Comision_BH, on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['comision_bh']) # simple
        ]
