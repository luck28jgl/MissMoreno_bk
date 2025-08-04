# filepath: c:\Users\JGL\Documents\repos_practica\MissAnaMoreno\Misanamoreno_bk\core\serializers.py
from rest_framework import serializers
from .models import usuario
from .models import *

class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

class bocabularioSerializer(serializers.ModelSerializer):

    class Meta:
        model = bocabulario
        fields = '__all__'

class abcedarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = abcedario
        fields = '__all__'

class usuariosSerializer(serializers.ModelSerializer):
    usr = AdminSerializer()  # Anidar el serializador para obtener más detalles del usuario

    class Meta:
        model = usuario
        fields = '__all__'

class TareasSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source='creado_por.usr.get_full_name', read_only=True)
    creado_por_email = serializers.EmailField(source='creado_por.usr.email', read_only=True)
    
    class Meta:
        model = tareas
        fields = '__all__'
        read_only_fields = ('fecha_creacion',)

class TareaAsignacionSerializer(serializers.ModelSerializer):
    tarea_nombre = serializers.CharField(source='tarea.nombre', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.usr.get_full_name', read_only=True)
    grupo_nombre = serializers.CharField(source='grupo.nombre', read_only=True)
    asignado_por_nombre = serializers.CharField(source='asignado_por.usr.get_full_name', read_only=True)
    
    class Meta:
        model = TareaAsignacion
        fields = '__all__'
        read_only_fields = ('fecha_asignacion',)

class TareaEntregaSerializer(serializers.ModelSerializer):
    tarea_nombre = serializers.CharField(source='asignacion.tarea.nombre', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.usr.get_full_name', read_only=True)
    puntos_maximos = serializers.IntegerField(source='asignacion.tarea.puntos_maximos', read_only=True)
    
    class Meta:
        model = TareaEntrega
        fields = '__all__'
        read_only_fields = ('fecha_entrega', 'fecha_modificacion')

class TareaReviewSerializer(serializers.ModelSerializer):
    revisor_nombre = serializers.CharField(source='revisor.usr.get_full_name', read_only=True)
    estudiante_nombre = serializers.CharField(source='entrega.estudiante.usr.get_full_name', read_only=True)
    tarea_nombre = serializers.CharField(source='entrega.asignacion.tarea.nombre', read_only=True)
    puntos_maximos = serializers.IntegerField(source='entrega.asignacion.tarea.puntos_maximos', read_only=True)
    
    class Meta:
        model = TareaReview
        fields = '__all__'
        read_only_fields = ('fecha_revision', 'fecha_modificacion')

class TareaEntregaConRevisionSerializer(serializers.ModelSerializer):
    """Serializer para entregas que incluye información de revisión"""
    revision = TareaReviewSerializer(read_only=True)
    tarea_nombre = serializers.CharField(source='asignacion.tarea.nombre', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.usr.get_full_name', read_only=True)
    puntos_maximos = serializers.IntegerField(source='asignacion.tarea.puntos_maximos', read_only=True)
    
    class Meta:
        model = TareaEntrega
        fields = '__all__'
        read_only_fields = ('fecha_entrega', 'fecha_modificacion')

class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = '__all__'
