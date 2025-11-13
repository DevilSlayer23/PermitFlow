
# from rest_framework import generics, mixins

# from authentication.models import Role, CustomUser as User
# from permits.models import Permit
# from applications.models import Status
# from payments.models import Payment, Transaction
# from applications.models import Application
# from .serializers import RoleSerializer, UserSerializer, PermitSerializer


# class RoleListCreateView(mixins.ListModelMixin,
#                          mixins.CreateModelMixin,
#                          generics.GenericAPIView):
    
#     queryset = Role.objects.all()
#     serializer_class = RoleSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)

# class UserListCreateView(mixins.ListModelMixin,
#                          mixins.CreateModelMixin,
#                          generics.GenericAPIView):
    
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)
    

# class ApplicationListCreateView(mixins.ListModelMixin,
#                          mixins.CreateModelMixin,
#                          generics.GenericAPIView):
    
#     queryset = Application.objects.all()
#     serializer_class = PermitSerializer

#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return self.create(request, *args, **kwargs)