# write a simple django view that returns a json response with a message "Hello, World!"
from django.http import JsonResponse
from django.views import View
from rest_framework.views import APIView

class HelloWorldView(APIView):
    def get(self, request):
        return JsonResponse({"message": "Hello, World!"})
    
