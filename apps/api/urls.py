from django.urls import include, path

# from .views import UserListCreateView

urlpatterns = [
    path('', include('apps.applications.urls')),
]
 