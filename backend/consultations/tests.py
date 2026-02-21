"""
Unit tests for the consultations app.
"""
import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from patients.models import Patient
from consultations.models import Consultation


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def patient(db):
    return Patient.objects.create(
        full_name="Alice Brown",
        date_of_birth="1988-07-22",
        email="alice@example.com",
    )


@pytest.fixture
def another_patient(db):
    return Patient.objects.create(
        full_name="Bob Green",
        date_of_birth="1975-11-10",
        email="bob@example.com",
    )


@pytest.fixture
def consultation(db, patient):
    return Consultation.objects.create(
        patient=patient,
        symptoms="Persistent headache and dizziness",
        diagnosis="Migraine",
    )


class TestConsultationCreate:
    def test_create_consultation_success(self, db, api_client, patient):
        url = reverse('consultation-list-create')
        payload = {
            "patient": patient.id,
            "symptoms": "Fever and sore throat",
            "diagnosis": "Strep throat",
        }
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert response.data['symptoms'] == payload['symptoms']
        assert response.data['patient'] == patient.id
        assert response.data['ai_summary'] is None

    def test_create_consultation_no_diagnosis(self, db, api_client, patient):
        """Diagnosis is optional."""
        url = reverse('consultation-list-create')
        payload = {"patient": patient.id, "symptoms": "Mild cough"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201

    def test_create_consultation_missing_symptoms(self, db, api_client, patient):
        url = reverse('consultation-list-create')
        payload = {"patient": patient.id}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_create_consultation_invalid_patient(self, db, api_client):
        url = reverse('consultation-list-create')
        payload = {"patient": 99999, "symptoms": "Some symptoms"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_create_consultation_blank_symptoms(self, db, api_client, patient):
        url = reverse('consultation-list-create')
        payload = {"patient": patient.id, "symptoms": "   "}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400


class TestConsultationList:
    def test_list_consultations(self, db, api_client, consultation):
        url = reverse('consultation-list-create')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_filter_by_patient(self, db, api_client, patient, another_patient):
        Consultation.objects.create(patient=patient, symptoms="Headache")
        Consultation.objects.create(patient=another_patient, symptoms="Backpain")
        url = reverse('consultation-list-create')

        response_1 = api_client.get(url, {'patient': patient.id})
        assert response_1.data['count'] == 1
        assert response_1.data['results'][0]['patient'] == patient.id

        response_2 = api_client.get(url, {'patient': another_patient.id})
        assert response_2.data['count'] == 1


class TestGenerateSummary:
    def test_generate_summary_mock(self, db, api_client, consultation):
        """Summary generation must succeed (using mock AI service)."""
        url = reverse('generate-summary', kwargs={'pk': consultation.pk})
        with patch('consultations.views.generate_consultation_summary') as mock_ai:
            mock_ai.return_value = "Chief Complaint:\n  Persistent headache and dizziness"
            response = api_client.post(url)

        assert response.status_code == 200
        assert response.data['ai_summary'] is not None
        assert 'headache' in response.data['ai_summary'].lower()

        # Verify it's persisted
        consultation.refresh_from_db()
        assert consultation.ai_summary is not None

    def test_generate_summary_not_found(self, db, api_client):
        url = reverse('generate-summary', kwargs={'pk': 99999})
        response = api_client.post(url)
        assert response.status_code == 404

    def test_generate_summary_updates_existing(self, db, api_client, consultation):
        """Calling generate-summary twice should update the existing summary."""
        url = reverse('generate-summary', kwargs={'pk': consultation.pk})
        with patch('consultations.views.generate_consultation_summary') as mock_ai:
            mock_ai.return_value = "First summary"
            api_client.post(url)
            mock_ai.return_value = "Updated summary"
            response = api_client.post(url)

        assert response.status_code == 200
        consultation.refresh_from_db()
        assert consultation.ai_summary == "Updated summary"
