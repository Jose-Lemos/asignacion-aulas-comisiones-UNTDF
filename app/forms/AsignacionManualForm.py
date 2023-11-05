from django import forms
from ..models import Carrera, Materia, Comision, Comision_BH, Aula, Asignacion


class AsignacionManualForm(forms.ModelForm):
    class Meta:
        model = Asignacion  # Utiliza tu modelo de asignación
        fields = [ 'aula','comision_bh'] 