from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth.models import User
# from cases.models import CaseAssignment
from cases.models import Detainee
from datetime import date


from django.test import TestCase
from cases.models import Detainee
from datetime import date
# from django.contrib.auth.models import User   # Uncomment later when user model is ready


class DetaineeModelTest(TestCase):

    def test_create_detainee(self):
        detainee = Detainee.objects.create(
            first_name="John",
            last_name="Doe",
            # user=self.user,  # commented out for now
            id_number="123456789",
            gender="male",
            date_of_birth=date(1995, 5, 17),
            relation_to_applicant="family"
        )
        self.assertEqual(detainee.first_name, "John")
        self.assertEqual(detainee.last_name, "Doe")
        self.assertEqual(detainee.id_number, "123456789")
        self.assertEqual(detainee.gender, "male")
        self.assertEqual(detainee.relation_to_applicant, "family")
        self.assertIsNotNone(detainee.created_at)

    def test_str_representation(self):
        detainee = Detainee.objects.create(
            first_name="Jane",
            last_name="Smith",
            # user=self.user,  # commented out for now
            id_number="987654321",
            gender="female",
            relation_to_applicant="other"
        )
        expected_str = f"Detainee {detainee.detainee_id}: Jane Smith (User None)"
        self.assertEqual(str(detainee), expected_str)

    def test_id_number_unique(self):
        Detainee.objects.create(
            first_name="Alice",
            last_name="Brown",
            id_number="9999",
            gender="male",
            relation_to_applicant="family"
        )
        with self.assertRaises(Exception):
            Detainee.objects.create(
                first_name="Bob",
                last_name="White",
                id_number="9999",  # duplicate
                gender="female",
                relation_to_applicant="other"
            )

    def test_optional_date_of_birth(self):
        detainee = Detainee.objects.create(
            first_name="NoDOB",
            last_name="Person",
            id_number="abc123",
            gender="male",
            relation_to_applicant="family"
        )
        self.assertIsNone(detainee.date_of_birth)

    # def test_foreign_key_relation(self):
    #     user = User.objects.create_user(username="testuser", password="testpass")
    #     detainee = Detainee.objects.create(
    #         first_name="FK",
    #         last_name="Tester",
    #         user=user,
    #         id_number="xyz789",
    #         gender="female",
    #         relation_to_applicant="family"
    #     )
    #     self.assertEqual(detainee.user.username, "testuser")



# class CaseAssignmentAPITest(APITestCase):
#    def setUp(self):
#        self.user = User.objects.create_user(username='assignuser', password='testpass')
#        self.client.login(username='assignuser', password='testpass')
#        self.detainee = Detainee.objects.create(
           
#            user=self.user,
#            id_number="D987654321",
#            gender="male",
#            relation_to_applicant="family"
#        )
#        self.case = Case.objects.create(
#            detainee=self.detainee,
#            case_description="Assignment test",
#            predicted_case_type="civil",
#            predicted_urgency_level="high",
#            latitude=1.2921,
#            longitude=36.8219,
#            stage="in_progress",
#            status="pending"
#        )


#    def test_post_caseassignment(self):
#        url = reverse('caseassignment-list')
#        data = {
#            "case": self.case.case_id,
#            "lawyer_id": 456,
#            "is_assigned": True
#        }
#        response = self.client.post(url, data, format='json')
#        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


#    def test_put_caseassignment(self):
#        assignment = CaseAssignment.objects.create(
#            case=self.case,
#            lawyer_id=456,
#            is_assigned=True
#        )
#        url = reverse('caseassignment-detail', args=[assignment.assignment_id])
#        data = {
#            "case": assignment.case.case_id,
#            "lawyer_id": assignment.lawyer_id,
#            "is_assigned": True,
#            "reject_reason": "Conflict of interest",
#            "confirmed_by_applicant": assignment.confirmed_by_applicant,
#            "confirmed_by_lawyer": False
#        }
#        response = self.client.put(url, data, format='json')
#        self.assertEqual(response.status_code, status.HTTP_200_OK)
#        assignment.refresh_from_db()
#        self.assertEqual(assignment.reject_reason, "Conflict of interest")


#    def test_delete_caseassignment(self):
#        assignment = CaseAssignment.objects.create(
#            case=self.case,
#            lawyer_id=456,
#            is_assigned=True
#        )
#        url = reverse('caseassignment-detail', args=[assignment.assignment_id])
#        response = self.client.delete(url)
#        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#        with self.assertRaises(CaseAssignment.DoesNotExist):
#            assignment.refresh_from_db()





