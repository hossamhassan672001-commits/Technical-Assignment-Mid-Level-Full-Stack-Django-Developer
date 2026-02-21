from patients.serializers import PatientSerializer
from rest_framework import serializers
from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):
    patient_details = PatientSerializer(source='patient', read_only=True)
    patient = serializers.PrimaryKeyRelatedField(
        queryset=__import__('patients.models', fromlist=['Patient']).Patient.objects.all(),
        write_only=False,
    )

    class Meta:
        model = Consultation
        fields = [
            'id',
            'patient',
            'patient_details',
            'symptoms',
            'diagnosis',
            'created_at',
            'ai_summary',
        ]
        read_only_fields = ['id', 'created_at', 'ai_summary']

    def validate_symptoms(self, value):
        if not value.strip():
            raise serializers.ValidationError("Symptoms cannot be blank.")
        return value.strip()
