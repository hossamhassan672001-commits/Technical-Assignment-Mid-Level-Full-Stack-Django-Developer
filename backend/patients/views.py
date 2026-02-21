from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/patients/  — list all patients (paginated)
    POST /api/patients/  — create a new patient
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'email']
    ordering_fields = ['full_name', 'date_of_birth']

    @swagger_auto_schema(
        operation_summary="List all patients",
        operation_description="Returns a paginated list of all patients. Supports search by name/email.",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by name or email", type=openapi.TYPE_STRING),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (e.g. full_name, -date_of_birth)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a patient",
        operation_description="Creates a new patient record. Email must be unique.",
        request_body=PatientSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
