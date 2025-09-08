from django.db import models
from django.contrib.auth.models import User
from django.db.models import JSONField


class Detainee(models.Model):
   detainee_id = models.AutoField(primary_key=True)
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
      return f"Detainee{self.detainee_id}(User {self.user_id or 'None'})"

    #    return f"Detainee {self.detainee_id} (User ID {self.user_id})"


