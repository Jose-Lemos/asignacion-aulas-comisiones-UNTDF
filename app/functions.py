from models import *


for p in Aula.objects.raw("Select * from App_Aula"): print(p)