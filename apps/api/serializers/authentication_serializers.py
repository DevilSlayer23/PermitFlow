
from authentication.models import Role, Department, CustomUser
from permits.models import Permit
from payments.models import  FeeSchedule, Payment, Transaction
from applications.models import Application, Applicant, Status
from reviews.models import Review
from rest_framework import serializers
from real_estate.models import Property

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
        model = CustomUser
        fields = '__all__'

""" End of Serializers for Application models"""
        


""" Serializers for Core models"""
        
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permit
        fields = '__all__'

class PermitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permit
        fields = '__all__'

""" End of Serializers for Core models"""



""" Serializers for Payments models"""

class FeeScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeSchedule
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







""" Serializers for Review models"""

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

""" End of Serializers for Review models"""



