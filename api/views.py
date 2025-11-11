
from rest_framework import generics, mixins

from users.models import Role, User
from core.models import Status, PermitType
from payments.models import FeeStructure, Payment, Transaction
from applications.models import Permit

from .serializers import RoleSerializer, DepartmentSerializer, UserSerializer, StatusSerializer, PermitTypeSerializer, PermitSerializer, FeeStructureSerializer, PaymentSerializer, TransactionSerializer


class RoleListCreateView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         generics.GenericAPIView):
    
    queryset = Role.objects.all()
    serializer_class = RoleSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class UserListCreateView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         generics.GenericAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)