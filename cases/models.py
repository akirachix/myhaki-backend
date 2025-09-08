from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField

class Case(models.Model):
    case_id = models.AutoField(primary_key=True)
    detainee_id = models.IntegerField()
    # detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, related_name='cases', null=True, blank=True)
    case_description = models.TextField()
    predicted_case_type = models.CharField(
        max_length=50,
        choices=[('criminal', 'Criminal'), ('civil', 'Civil'), ('other', 'Other')],
        null=True,
        blank=True
    )
    predicted_urgency_level = models.CharField(
        max_length=20,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        null=False
    )
    date_of_offense = models.DateField(null=True, blank=True)
    trial_date = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    monthly_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    income_source = models.CharField(max_length=100, null=True, blank=True)
    dependents = JSONField(null=True, blank=True, default=dict)
    stage = models.CharField(
        max_length=50,
        choices=[('in_progress', 'In Progress'), ('handled', 'Handled'), ('arraignment', 'Arraignment'),
                 ('bail', 'Bail'), ('trial', 'Trial'), ('completed', 'Completed')],
        null=False
    )
    status = models.CharField(
        max_length=50,
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')],
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['detainee_id', 'case_description', 'trial_date'],
                name='unique_case_per_detainee_description_trialdate'
            )
        ]