from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Consultation
from .serializers import ConsultationSerializer
from .services.ai_service import generate_consultation_summary


class ConsultationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/consultations/           — list all consultations (paginated)
    GET  /api/consultations/?patient=1 — filter by patient ID
    POST /api/consultations/           — create a new consultation
    """
    serializer_class = ConsultationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['symptoms', 'diagnosis', 'patient__full_name']
    ordering_fields = ['created_at', 'patient__full_name']

    def get_queryset(self):
        queryset = Consultation.objects.select_related('patient').all()
        patient_id = self.request.query_params.get('patient')
        if patient_id is not None:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

    @swagger_auto_schema(
        operation_summary="List consultations",
        operation_description="Returns a paginated list of consultations. Filter by patient using ?patient=<id>.",
        manual_parameters=[
            openapi.Parameter('patient', openapi.IN_QUERY, description="Filter by patient ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in symptoms, diagnosis, patient name", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a consultation",
        operation_description="Creates a new consultation for a given patient.",
        request_body=ConsultationSerializer,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GenerateSummaryView(APIView):
    """
    POST /api/consultations/{id}/generate-summary/

    Calls the AI service to generate a structured clinical summary
    from the consultation's symptoms and diagnosis, stores it, and
    returns the updated consultation object.
    """

    @swagger_auto_schema(
        operation_summary="Generate AI summary",
        operation_description=(
            "Triggers AI summary generation for the specified consultation. "
            "Uses OpenAI if OPENAI_API_KEY is set; otherwise returns a realistic mock summary. "
            "Stores the result in `ai_summary` and returns the full consultation object."
        ),
        responses={
            200: ConsultationSerializer,
            404: openapi.Response(description="Consultation not found"),
            500: openapi.Response(description="AI service error"),
        },
    )
    def post(self, request, pk):
        consultation = get_object_or_404(Consultation, pk=pk)

        try:
            summary = generate_consultation_summary(
                symptoms=consultation.symptoms,
                diagnosis=consultation.diagnosis,
            )
        except Exception as exc:
            return Response(
                {'error': True, 'message': f'AI service error: {str(exc)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        consultation.ai_summary = summary
        consultation.save(update_fields=['ai_summary'])

        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data, status=status.HTTP_200_OK)
