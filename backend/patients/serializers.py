from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'full_name', 'date_of_birth', 'email']

    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Full name cannot be blank.")
        return value.strip()

    def validate_email(self, value):
        return value.lower().strip()
