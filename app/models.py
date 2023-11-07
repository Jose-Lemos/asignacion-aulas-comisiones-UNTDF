from django.db import models

class Herramienta(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    #cantidad = models.IntegerField(default=1)
    #pk = models.AutoField(primary_key=True) # integer: autoincremental
    # proyector = models.BooleanField()
    # polycom = models.BooleanField()
    # televisor = models.BooleanField()
    # computadoras = models.BooleanField()

    def __str__(self) :
        return self.nombre

    class Meta: # Los índices van a ayudar al momento de recorrer las asignaciones, cuando busquemos las aulas vacías para el periodo actual
        indexes = [
            models.Index(fields=['id', 'nombre']), # compuesto
        ]

class Aula(models.Model):
    #pk = models.IntegerField(primary_key=True) # espacio o integer: nuestro, sin consumirlas, sino cargandolas nososotros
    nombre = models.CharField(max_length=255, unique=True) # nombre o string: nuestro
    cant_cupos = models.IntegerField()
     

    tipos = [("COMUN", "Comun"),
             ("LABORATORIO", "Laboratorio"),
             ("MODULO", "Modulo"),
             ("OFICINA", "Oficina")
    ]
    
    tipo = models.CharField(max_length=20, choices=tipos, default="COMUN")
    herramientas = models.ManyToManyField(Herramienta, blank=True)#Verificar el modelo, queremos el booleano o el texto de las herramientas

    def __str__(self) :
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['id', 'nombre']), # compuesto
        ]

class Carrera(models.Model):
    # Recordar hacer coincidir la PK de Materia con el id de Elemento en Guaraní
    #pk = models.IntegerField(primary_key=True) # elemento
    nombre = models.CharField(max_length=255, unique=True) # nombre
    #codigo = models.CharField(max_length=20, unique=True) # codigo

    tipos = [("LICENCIATURA", "Licenciatura"),
             ("TECNICATURA", "Tecnicatura"),
             ("POSTGRADO", "Postgrado"),
             ("MAESTRIA", "Maestria")
    ]
    
    tipo = models.CharField(max_length=20, choices=tipos, default="LICENCIATURA", null=True)

    def __str__(self) :
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['id', 'nombre']), # compuesto
        ]

class Materia(models.Model):
    # Recordar hacer coincidir la PK de Materia con el id de Elemento en Guaraní
    #pk = models.IntegerField(primary_key=True) # elemento
    nombre = models.CharField(max_length=255) # nombre
    #codigo = models.CharField(max_length=20, unique=True) # codigo --> El SIU Guaraní está mal cargado. Hay nombres de materias con códigos repetidos. Decidimos manejarlos solamente con los ids
    carrera = models.ManyToManyField(Carrera)# string: simplificamos datos, se puede obtener de sga_elementos_plan.plan_version.nombre

    def __str__(self) :
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['id', 'nombre']), # compuesto
        ]

class Comision(models.Model):
    #pk = models.IntegerField(primary_key=True) # comision
    nombre = models.CharField(max_length=100, unique=True) # nombre
    cant_insc = models.IntegerField() # consulta sobre sga_insc_cursada. Tiene ser UPDATE cada nuevo consumo que se haga = sga_insc_cursada.comision JOIN (sga_comisiones_bh.asignacion.fecha_desde >= currentDate())
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    # aula_preferida = models.ForeignKey(Aula, on_delete=models.CASCADE, null=True) # No sé si realmente es necesaria. Las predefinidas las podemos cargar a mano, y luego correr el algoritmo sobre estas. Para esto hay que tener en cuenta que el 
    comision_compartida = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    preferencias = models.ManyToManyField(Herramienta, blank=True)
    requiere_aula_exclusiva = models.BooleanField(default=False)

    def __str__(self) :
        return self.nombre

    class Meta:
        indexes = [
            models.Index(fields=['id', 'nombre']), # compuesto
        ]

class Comision_BH(models.Model): # Misma lógica de consumo que para la cant_insc --> sga_insc_cursada.comision JOIN (sga_comisiones_bh.asignacion.fecha_desde >= currentDate())
    #pk = models.AutoField(primary_key=True)
    comision = models.ForeignKey(Comision, on_delete=models.CASCADE, null=True, to_field='nombre')
    #to_field se agrega para mapear por ese atributo
    #comision_nombre = models.CharField(max_length=100)  # Campo para almacenar el nombre de la comisión
    
    dia = models.CharField(max_length=9)
    hora_ini = models.TimeField()
    hora_fin = models.TimeField()
    fecha_ini = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self) :
        return "{0}-{1}-{2}-{3}".format(self.comision.__str__(), self.dia, self.hora_ini, self.hora_fin)

    class Meta:
        indexes = [
            models.Index(fields=['id', 'fecha_fin']), # compuesto
        ]

class Asignacion(models.Model):
    #pk = models.AutoField(primary_key=True)
    aula =  models.ForeignKey(Aula, on_delete=models.CASCADE, null=True)
    comision_bh =  models.ForeignKey(Comision_BH, on_delete=models.CASCADE, null=True)

    def get_com(self):
        return self.comision_bh.id

    def __str__(self):
        return "{0}-{1}-{2}".format(self.id, self.aula, self.comision_bh)

    class Meta:
        indexes = [
            models.Index(fields=['comision_bh']) # simple
        ]

    class Meta:
        indexes = [
            models.Index(fields=['comision_bh']) # simple
        ]
