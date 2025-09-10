from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from cases.models import Case, Detainee
from datetime import date
from unittest.mock import patch
import json
from django.contrib.auth import get_user_model

User = get_user_model()
class MyTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_example(self):
        self.assertTrue(self.user.is_authenticated)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


def mock_translate_side_effect(*args, **kwargs):
    payload = kwargs.get('json', {})
    text = payload.get('text', '')

    if text == "Aliiba mahindi ya jirani usiku wa manane.":
        return MockResponse({
            "translations": {
                "translation": "He stole his neighbor's corn in the middle of the night."
            }
        }, 200)
    elif text == "Kituo cha Polisi Machakos":
        return MockResponse({
            "translations": {
                "translation": "Machakos Police Station"
            }
        }, 200)
    elif text == json.dumps({"count": 3, "description": "watoto watatu"}):
        return MockResponse({
            "translations": {
                "translation": json.dumps({"count": 3, "description": "three children"})
            }
        }, 200)
    else:
        return MockResponse({
            "translations": {
                "translation": text
            }
        }, 200)


class CaseAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.detainee = Detainee.objects.create(
            first_name='Jane',
            last_name='Doe',
            user=self.user,
            id_number='ID123456',
            gender='female',
            relation_to_applicant='family'
        )
        self.client.login(username='testuser', password='testpass')

    @patch('api.serializers.requests.post')
    @patch('api.serializers.requests.get')
    def test_post_case(self, mock_get, mock_post):
        mock_post.side_effect = mock_translate_side_effect
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {'lat': '-1.5176837', 'lon': '37.2634146'}
        ]

        url = reverse('case-list')
        data = {
            "detainee": self.detainee.detainee_id,
            "case_description": "Aliiba mahindi ya jirani usiku wa manane.",
            "predicted_case_type": "civil",
            "predicted_urgency_level": "high",
            "date_of_offense": "2025-01-01",
            "trial_date": "2025-06-01",
            "police_station": "Kituo cha Polisi Machakos",
            "monthly_income": "less_than_30000",
            "income_source": "informal",
            "dependents": {"count": 3, "description": "watoto watatu"},
            "stage": "in_progress",
            "status": "pending"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['case_description'], "He stole his neighbor's corn in the middle of the night.")
        self.assertEqual(response.data['police_station'], 'Machakos Police Station')
        self.assertAlmostEqual(float(response.data['latitude']), -1.5176837, places=6)
        self.assertAlmostEqual(float(response.data['longitude']), 37.2634146, places=6)
        self.assertEqual(response.data['dependents']['count'], 3)
        self.assertEqual(response.data['dependents']['description'], 'three children')

    def test_post_case_invalid_monthly_income(self):
        url = reverse('case-list')
        data = {
            "detainee": self.detainee.detainee_id,
            "case_description": "He had a fight in a bar",
            "predicted_case_type": "criminal",
            "predicted_urgency_level": "high",
            "date_of_offense": "2025-01-01",
            "trial_date": "2025-06-01",
            "latitude": 1.2921,
            "longitude": 36.8219,
            "monthly_income": "greater_than_30000",
            "income_source": "formal",
            "dependents": {"count": 2, "description": "Two kids"},
            "stage": "in_progress",
            "status": "pending"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('monthly_income', response.data)
        self.assertEqual(
            response.data['monthly_income'][0],
            "You are not eligible for this service"
        )

    def test_get_case(self):
        case = Case.objects.create(
            detainee=self.detainee,
            case_description= "He had a fight in a bar",
            predicted_case_type= "criminal",
            predicted_urgency_level= "high",
            date_of_offense= "2025-01-01",
            trial_date= "2025-06-01",
            police_station= "Kituo cha Polisi Machakos",
            monthly_income= "greater_than_30000",
            income_source= "formal",
            dependents= {"count": 2, "description": "Two kids"},
            stage= "in_progress",
            status= "pending"
        )
        url = reverse('case-detail', args=[case.case_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['case_description'], "He had a fight in a bar")
        self.assertEqual(response.data['predicted_case_type'], "criminal")
        self.assertEqual(response.data['predicted_urgency_level'], "high")
        self.assertEqual(response.data['date_of_offense'], "2025-01-01")
        self.assertEqual(response.data['trial_date'], "2025-06-01")
        self.assertEqual(response.data['police_station'], "Kituo cha Polisi Machakos")
        self.assertEqual(response.data['monthly_income'], "greater_than_30000")
        self.assertEqual(response.data['income_source'], "formal")
        self.assertEqual(response.data['dependents'], {"count": 2, "description": "Two kids"})
        self.assertEqual(response.data['stage'], "in_progress")
        self.assertEqual(response.data['status'], "pending")

    @patch('api.serializers.requests.post')
    def test_update_case(self, mock_post):
        mock_post.side_effect = mock_translate_side_effect

        case = Case.objects.create(
            detainee=self.detainee,
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
            "detainee": self.detainee.detainee_id,
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data['monthly_income'] = 'less_than_30000'
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        case.refresh_from_db()
        self.assertEqual(case.case_description, "Updated description")
        self.assertEqual(case.status, "accepted")


class DetaineeModelTest(TestCase):
    def test_create_detainee(self):
        detainee = Detainee.objects.create(
            first_name="John",
            last_name="Doe",
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
            first_name="lwam",
            last_name="bisrat",
            id_number="987654321",
            gender="female",
            relation_to_applicant="other"
        )
        expected_str = f"Detainee {detainee.detainee_id}: lwam bisrat (User None)"
        self.assertEqual(str(detainee), expected_str)

    def test_id_number_unique(self):
        Detainee.objects.create(
            first_name="meri",
            last_name="bisrat",
            id_number="9999",
            gender="male",
            relation_to_applicant="family"
        )
        with self.assertRaises(Exception):
            Detainee.objects.create(
                first_name="Betty",
                last_name="White",
                id_number="9999",
                gender="female",
                relation_to_applicant="other"
            )

    def test_optional_date_of_birth(self):
        detainee = Detainee.objects.create(
            first_name="lily",
            last_name="berhe",
            id_number="abc123",
            gender="male",
            relation_to_applicant="family"
        )
        self.assertIsNone(detainee.date_of_birth)


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