from django.contrib.postgres.operations import HStoreExtension, UnaccentExtension
from django.contrib.postgres.fields import HStoreField
from django.contrib.auth.models import User
from django.db import models, migrations
# Create your models here.
class Migration(migrations.Migration):
	operations = [
		HStoreExtension(),
		UnaccentExtension(),
	]

class usuario(models.Model):
    class TiposUsuario(models.IntegerChoices):
        MAESTRO = 1
        ALUMNO = 2
    usr = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    tipo_usuario = models.IntegerField(
    choices=TiposUsuario.choices, default=TiposUsuario.ALUMNO)
    tareastes = models.ForeignKey('tareas', on_delete=models.CASCADE, null=True)
    bocabularioasing = models.ForeignKey('bocabulario', on_delete=models.CASCADE, null=True)
    grupo = models.ForeignKey('Grupo', on_delete=models.SET_NULL, null=True, blank=True)
    grado = models.IntegerField(default=0)

class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tareas = models.ManyToManyField('tareas', blank=True)

class bocabulario(models.Model):
    nombre = models.CharField(max_length=300, default='')
    descripcion = models.CharField(max_length=300, default='')
    texturl = models.CharField(max_length=200, default='')
    texestanol = models.CharField(max_length=200, default='')
    texingles = models.CharField(max_length=200, default='')
    publico = models.BooleanField(default=False)
    tipo = models.IntegerField(default=0)

class abcedario(models.Model):
    texturl = models.CharField(max_length=200, default='')
    texestanol = models.CharField(max_length=200, default='')
    texingles = models.CharField(max_length=200, default='')
    publico = models.BooleanField(default=False)

class tareas(models.Model):
    nombre = models.CharField(max_length=300, default='')
    descripcion = models.CharField(max_length=300, default='')
    es_general = models.BooleanField(default=False)

class habilidadverbal(models.Model):
    calificacion_max = models.CharField(max_length=300, default='')
    caliicacion_minima = models.CharField(max_length=300, default='')
    fecha_entrega = models.DateTimeField(null=True)