from users.models import Role, Department, User
from core.models import Status, PermitType, Permit
from payments.models import FeeStructure, Payment, Transaction
from applications.models import Application, Applicant, Property
from reviews.models import Review
from rest_framework import serializers


""" Serializers for User models"""

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

""" End of Serializers for Application models"""
        


""" Serializers for Core models"""
        
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class PermitTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermitType
        fields = '__all__'

class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permit
        fields = '__all__'

""" End of Serializers for Core models"""



""" Serializers for Payments models"""

class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

""" End of Serializers for Payments models"""



""" Serializers for Application models"""

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'

""" End of Serializers for Application models"""



""" Serializers for Review models"""

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

""" End of Serializers for Review models"""



