from django.urls import path
from .views import ConsultationListCreateView, GenerateSummaryView

urlpatterns = [
    path('consultations/', ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<int:pk>/generate-summary/', GenerateSummaryView.as_view(), name='generate-summary'),
]
