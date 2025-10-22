from django.db import models
from users.models import LawyerProfile

# cpd points models
class CPDPoint(models.Model):
    cpd_id = models.AutoField(primary_key=True)
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, null=True, blank=True)
    case = models.ForeignKey('cases.Case', on_delete=models.CASCADE, related_name='points')
    description = models.TextField(null=True, blank=True)
    points_earned = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cpd_point'
        verbose_name = 'CPD Point'
        verbose_name_plural = 'CPD Points'

    def __str__(self):
        return f"CPD {self.cpd_id} for Lawyer {self.lawyer} - {self.points_earned} points"
    
    