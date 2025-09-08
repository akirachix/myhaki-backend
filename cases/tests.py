from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from cases.models import Case


class CaseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_post_case(self):
        url = reverse('case-list')
        data = {
            "detainee_id": 123,
            "case_description": "Test case description",
            "predicted_case_type": "civil",
            "predicted_urgency_level": "high",
            "date_of_offense": "2025-01-01",
            "trial_date": "2025-06-01",
            "latitude": 1.2921,
            "longitude": 36.8219,
            "monthly_income": "less_than_30000",
            "income_source": "informal",
            "dependents": {"count": 2, "description": "Two kids"},
            "stage": "in_progress",
            "status": "pending"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.case_id = response.data['case_id']

    def test_get_case(self):
        case = Case.objects.create(
            detainee_id=123,
            case_description="Retrieve test",
            predicted_case_type="civil",
            predicted_urgency_level="high",
            latitude=1.2921,
            longitude=36.8219,
            monthly_income="less_than_30000",
            income_source="informal",
            stage="in_progress",
            status="pending"
        )
        url = reverse('case-detail', args=[case.case_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['case_description'], "Retrieve test")

    def test_update_case(self):
        case = Case.objects.create(
            detainee_id=123,
            case_description="Old description",
            predicted_case_type="civil",
            predicted_urgency_level="high",
            latitude=1.2921,
            longitude=36.8219,
            monthly_income="less_than_30000",
            income_source="informal",
            stage="in_progress",
            status="pending"
        )
        url = reverse('case-detail', args=[case.case_id])
        data = {
            "detainee_id": 123,
            "case_description": "Updated description",
            "predicted_case_type": "criminal",
            "predicted_urgency_level": "medium",
            "date_of_offense": "2025-02-01",
            "trial_date": "2025-07-01",
            "latitude": 1.2922,
            "longitude": 36.8220,
            "monthly_income": "greater_than_30000",
            "income_source": "formal",
            "dependents": {"count": 3, "description": "Three kids"},
            "stage": "handled",
            "status": "accepted"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        case.refresh_from_db()
        self.assertEqual(case.case_description, "Updated description")
        self.assertEqual(case.status, "accepted")




            
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth.models import User
# from cases.models import CaseAssignment



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


