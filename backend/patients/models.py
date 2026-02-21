from django.db import models


class Patient(models.Model):
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.email})"
