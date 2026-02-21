from django.db import models
from patients.models import Patient


class Consultation(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='consultations'
    )
    symptoms = models.TextField()
    diagnosis = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    ai_summary = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Consultation #{self.id} — {self.patient.full_name} ({self.created_at.date()})"
