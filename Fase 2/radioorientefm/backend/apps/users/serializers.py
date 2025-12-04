from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Credenciales inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Cuenta desactivada.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email y contraseña son requeridos.')

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'full_name', 'is_active', 'is_staff', 'fecha_creacion')
        read_only_fields = ('id', 'is_active', 'is_staff', 'fecha_creacion')

#serializers de compatibilidad para el frontend existente
class UserLegacySerializer(serializers.ModelSerializer):
    """serializer para mantener compatibilidad con el frontend existente"""
    correo = serializers.CharField(source='email', read_only=True)
    usuario = serializers.CharField(source='username', read_only=True)
    nombre = serializers.CharField(source='full_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'correo', 'usuario', 'nombre', 'first_name', 'last_name', 'is_active', 'is_staff', 'fecha_creacion')

class PasswordResetRequestSerializer(serializers.Serializer):
    """serializer para solicitar el reseteo de contraseña"""
    email = serializers.EmailField()

    #nota de seguridad: no validamos si el email existe en la base de datos
    #para prevenir user enumeration attacks. la vista manejará esto de forma segura

class PasswordResetConfirmSerializer(serializers.Serializer):
    """serializer para confirmar el reseteo de contraseña con token"""
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})

        try:
            uid = urlsafe_base64_decode(attrs['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uid": "Token inválido."})

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError({"token": "Token inválido o expirado."})

        attrs['user'] = user
        return attrs
