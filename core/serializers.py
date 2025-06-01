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
