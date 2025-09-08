from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField




class CaseAssignment(models.Model):
   assignment_id = models.AutoField(primary_key=True)
   lawyer_id = models.IntegerField()
   # lawyer = models.ForeignKey(
   #     'lawyer.Lawyer',
   #     on_delete=models.CASCADE,
   #     related_name='assignments'
   # )
#    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='assignments')
   case_id = models.IntegerField()
   is_assigned = models.BooleanField(default=True)
   assign_date = models.DateTimeField(auto_now_add=True)
   reject_reason = models.TextField(null=True, blank=True)
   confirmed_by_applicant = models.BooleanField(default=False)
   confirmed_by_lawyer = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)






