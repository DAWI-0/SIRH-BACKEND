from rest_framework import serializers
from .models import Employe, ManagerRH

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ['id', 'username', 'email', 'password', 'matricule', 'poste_titre']
        extra_kwargs = {'password': {'write_only': True}} # Password won't be returned in API response

    def create(self, validated_data):
        password = validated_data.pop('password')
        # Create the instance
        employe = Employe(**validated_data)
        # Safely hash the password
        employe.set_password(password)
        # Force the role
        employe.role = 'EMPLOYE'
        employe.save()
        return employe

class ManagerRHSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerRH
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        manager = ManagerRH(**validated_data)
        manager.set_password(password)
        manager.role = 'RH'
        manager.is_staff = True # Optional: allows HR to access Django Admin if needed
        manager.save()
        return manager