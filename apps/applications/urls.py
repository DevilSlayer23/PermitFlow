# Create a router for the applications app
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplciationViewSet


urlpatterns = [
    path('applications/', ApplciationViewSet.as_view({'get': 'list', 'post': 'create'}), name='application-list'),
    path('applications/<str:pk>/', ApplciationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='application-detail'),
]
