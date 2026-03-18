"""
Serializadores para usuarios.
"""

from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializador completo de usuario."""
    
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'nombre_completo', 'rol', 'rol_display', 'unidad',
            'programa_educativo', 'telefono', 'is_active'
        ]
        read_only_fields = ['id', 'username']
    
    def get_nombre_completo(self, obj):
        return obj.get_full_name()


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializador para login."""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializador para crear usuarios."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'rol', 'unidad',
            'programa_educativo', 'telefono'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario
