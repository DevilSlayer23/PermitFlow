from rest_framework import serializers
from applications.models import Applicant, Application
from apps.real_estate.models import RealEstate

""" Serializers for Application models"""

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'  
    
class ApplicationListSerializer(serializers.ModelSerializer):
    applicant = ApplicantSerializer()
    class Meta:
        model = Application
        fields = ['id', 'application_number', 'applicant', 'status', 'created_at']

class ApplicationDetailSerializer(serializers.ModelSerializer):
    applicants = ApplicantSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = '__all__'