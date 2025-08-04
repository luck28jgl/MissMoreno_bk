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
    bocabularioasing = models.ForeignKey('bocabulario', on_delete=models.CASCADE, null=True)
    grupo = models.ForeignKey('Grupo', on_delete=models.SET_NULL, null=True, blank=True)
    grado = models.IntegerField(default=0)
    materia_a_impartir = models.TextField(default='', null=True, blank=True)
    grado_a_impartir = models.TextField(default='', null=True, blank=True)
    grupo_aimpartir = models.IntegerField(default=0, null=True, blank=True)

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
    class EstadoTarea(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        PUBLICADA = 'PUBLICADA', 'Publicada'
        CERRADA = 'CERRADA', 'Cerrada'
    
    nombre = models.CharField(max_length=300, default='')
    descripcion = models.TextField(default='')
    instrucciones = models.TextField(blank=True, null=True)
    es_general = models.BooleanField(default=False)
    creado_por = models.ForeignKey('usuario', on_delete=models.CASCADE, related_name='tareas_creadas', null=True, blank=True)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True)
    puntos_maximos = models.IntegerField(default=100)
    estado = models.CharField(max_length=20, choices=EstadoTarea.choices, default=EstadoTarea.BORRADOR)
    archivo_adjunto = models.CharField(max_length=500, blank=True, null=True)  # URL del archivo
    
    def save(self, *args, **kwargs):
        if not self.fecha_creacion:
            from django.utils import timezone
            self.fecha_creacion = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        creador = self.creado_por.usr.username if self.creado_por else "Sin asignar"
        return f"{self.nombre} - {creador}"

class habilidadverbal(models.Model):
    calificacion_max = models.CharField(max_length=300, default='')
    caliicacion_minima = models.CharField(max_length=300, default='')
    fecha_entrega = models.DateTimeField(null=True)


class TareaAsignacion(models.Model):
    class EstadoAsignacion(models.TextChoices):
        ASIGNADA = 'ASIGNADA', 'Asignada'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        ENTREGADA = 'ENTREGADA', 'Entregada'
        REVISADA = 'REVISADA', 'Revisada'
        CALIFICADA = 'CALIFICADA', 'Calificada'
    
    tarea = models.ForeignKey('tareas', on_delete=models.CASCADE, related_name='asignaciones')
    estudiante = models.ForeignKey('usuario', on_delete=models.CASCADE, related_name='tareas_asignadas', null=True, blank=True)
    grupo = models.ForeignKey('Grupo', on_delete=models.CASCADE, related_name='tareas_asignadas', null=True, blank=True)
    asignado_por = models.ForeignKey('usuario', on_delete=models.CASCADE, related_name='asignaciones_realizadas')
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento_personalizada = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoAsignacion.choices, default=EstadoAsignacion.ASIGNADA)
    
    def save(self, *args, **kwargs):
        if not self.fecha_asignacion:
            from django.utils import timezone
            self.fecha_asignacion = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [['tarea', 'estudiante'], ['tarea', 'grupo']]
    
    def __str__(self):
        target = self.estudiante.usr.username if self.estudiante else self.grupo.nombre
        return f"{self.tarea.nombre} -> {target}"


class TareaEntrega(models.Model):
    class EstadoEntrega(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        ENTREGADA = 'ENTREGADA', 'Entregada'
        REVISANDO = 'REVISANDO', 'En Revisión'
        CALIFICADA = 'CALIFICADA', 'Calificada'
    
    asignacion = models.ForeignKey('TareaAsignacion', on_delete=models.CASCADE, related_name='entregas')
    estudiante = models.ForeignKey('usuario', on_delete=models.CASCADE, related_name='entregas_realizadas')
    contenido = models.TextField()
    archivo_adjunto = models.CharField(max_length=500, blank=True, null=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=EstadoEntrega.choices, default=EstadoEntrega.BORRADOR)
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.fecha_entrega:
            self.fecha_entrega = timezone.now()
        self.fecha_modificacion = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.asignacion.tarea.nombre} - {self.estudiante.usr.username}"


class TareaReview(models.Model):
    entrega = models.OneToOneField('TareaEntrega', on_delete=models.CASCADE, related_name='revision')
    revisor = models.ForeignKey('usuario', on_delete=models.CASCADE, related_name='revisiones_realizadas')
    calificacion = models.IntegerField(null=True, blank=True)  # Puntos obtenidos
    comentarios = models.TextField(blank=True, null=True)
    fecha_revision = models.DateTimeField(null=True, blank=True)
    fecha_modificacion = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        if not self.fecha_revision:
            self.fecha_revision = timezone.now()
        self.fecha_modificacion = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Revisión: {self.entrega.asignacion.tarea.nombre} - {self.entrega.estudiante.usr.username}"