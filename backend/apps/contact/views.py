from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import ContactMessage, Subscription
from .serializers import ContactMessageSerializer, SubscriptionSerializer

class ContactMessageCreateView(generics.CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe(request):
    serializer = SubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        subscription, created = Subscription.objects.get_or_create(
            email=email,
            defaults={'name': serializer.validated_data.get('name', '')}
        )
        if created:
            return Response({'message': 'Suscripción exitosa'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Ya estás suscrito'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe(request):
    email = request.data.get('email')
    if email:
        try:
            subscription = Subscription.objects.get(email=email)
            subscription.is_active = False
            subscription.save()
            return Response({'message': 'Desuscripción exitosa'})
        except Subscription.DoesNotExist:
            return Response({'error': 'Email no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Email requerido'}, status=status.HTTP_400_BAD_REQUEST)
