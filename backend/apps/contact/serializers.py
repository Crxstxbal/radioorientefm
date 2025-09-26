from rest_framework import serializers
from .models import ContactMessage, Subscription

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['nombre', 'correo', 'telefono', 'asunto', 'mensaje']

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['correo', 'nombre']
