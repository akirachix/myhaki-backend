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
   case = models.ForeignKey('cases.Case', on_delete=models.CASCADE, related_name='assignments')
   is_assigned = models.BooleanField(default=True)
   assign_date = models.DateTimeField(auto_now_add=True)
   reject_reason = models.TextField(null=True, blank=True)
   confirmed_by_applicant = models.BooleanField(default=False)
   confirmed_by_lawyer = models.BooleanField(default=False)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)



class Detainee(models.Model):
   detainee_id = models.AutoField(primary_key=True)
   first_name = models.CharField(max_length=100, null=False, blank=False)
   last_name = models.CharField(max_length=100, null=False, blank=False)


   user = models.ForeignKey(
       User,
       on_delete=models.CASCADE,
       null=True,
       blank=True
    #    limit_choices_to={'role': 'applicant'}
   )
   id_number = models.CharField(max_length=50, null=True, blank=True, unique=True)
   gender = models.CharField(
       max_length=20,
       choices=[('male', 'Male'), ('female', 'Female')]
   )
   date_of_birth = models.DateField(null=True, blank=True)
   relation_to_applicant = models.CharField(
       max_length=50,
       choices=[('family', 'Family'), ('other', 'Other')]
   )
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)


   def __str__(self):
        return f"Detainee {self.detainee_id}: {self.first_name} {self.last_name} (User {self.user_id or 'None'})"

class Case(models.Model):
    case_id = models.AutoField(primary_key=True)
    detainee = models.ForeignKey(Detainee, on_delete=models.CASCADE, related_name='cases', null=True, blank=True)
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

    income_source = models.CharField(
        max_length=10,
        choices=[('informal', 'Informal'), ('formal', 'Formal')],
        null=True,
        blank=True
    )

    monthly_income = models.CharField(
        max_length=20,
        choices=[('less_than_30000', 'Less than 30000'), ('greater_than_30000', 'Greater than 30000')],
        null=True,
        blank=True
    )

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


