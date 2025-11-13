from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import viewsets
from applications.models import Application
from api.serializers import ApplicationSerializer

class ApplciationViewSet(viewsets.ModelViewSet):

    queryset = Application.objects.all()

    def list(self, request):
        serializer = ApplicationSerializer(self.queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = ApplicationSerializer(item)
        return Response(serializer.data)

    def create(self, request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        item = get_object_or_404(self.queryset, pk=pk)
        serializer = ApplicationSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApplicationSerializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            if instance is None:
                lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
                lookup_value = self.kwargs[lookup_url_kwarg]
                extra_kwargs = {self.lookup_field: lookup_value}
                serializer.save(**extra_kwargs)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated] # Default for other actions

        return [permission() for permission in permission_classes]