"""
Unit tests for the patients app.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from patients.models import Patient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_patient(db):
    return Patient.objects.create(
        full_name="Jane Doe",
        date_of_birth="1990-05-15",
        email="jane@example.com",
    )


@pytest.fixture
def patient_payload():
    return {
        "full_name": "John Smith",
        "date_of_birth": "1985-03-20",
        "email": "john.smith@example.com",
    }


class TestPatientCreate:
    def test_create_patient_success(self, db, api_client, patient_payload):
        url = reverse('patient-list-create')
        response = api_client.post(url, patient_payload, format='json')
        assert response.status_code == 201
        assert response.data['full_name'] == patient_payload['full_name']
        assert response.data['email'] == patient_payload['email'].lower()

    def test_create_patient_missing_full_name(self, db, api_client):
        url = reverse('patient-list-create')
        payload = {"date_of_birth": "1990-01-01", "email": "test@example.com"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_create_patient_missing_email(self, db, api_client):
        url = reverse('patient-list-create')
        payload = {"full_name": "Test User", "date_of_birth": "1990-01-01"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_create_patient_invalid_email(self, db, api_client):
        url = reverse('patient-list-create')
        payload = {"full_name": "Test", "date_of_birth": "1990-01-01", "email": "not-an-email"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 400

    def test_create_patient_duplicate_email(self, db, api_client, sample_patient, patient_payload):
        """Duplicate email must return 400."""
        url = reverse('patient-list-create')
        patient_payload['email'] = sample_patient.email
        response = api_client.post(url, patient_payload, format='json')
        assert response.status_code == 400

    def test_create_patient_email_normalized(self, db, api_client):
        url = reverse('patient-list-create')
        payload = {"full_name": "Case Test", "date_of_birth": "2000-01-01", "email": "UPPER@EXAMPLE.COM"}
        response = api_client.post(url, payload, format='json')
        assert response.status_code == 201
        assert response.data['email'] == 'upper@example.com'


class TestPatientList:
    def test_list_patients_empty(self, db, api_client):
        url = reverse('patient-list-create')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 0

    def test_list_patients_with_data(self, db, api_client, sample_patient):
        url = reverse('patient-list-create')
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1

    def test_search_patient_by_email(self, db, api_client, sample_patient):
        url = reverse('patient-list-create')
        response = api_client.get(url, {'search': 'jane@example.com'})
        assert response.status_code == 200
        assert response.data['count'] == 1
