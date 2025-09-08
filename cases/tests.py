from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from cases.models import Case, Detainee
from datetime import date


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

    def test_post_case(self):
        url = reverse('case-list')
        data = {
            "detainee": self.detainee.detainee_id,
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

    def test_post_case_invalid_monthly_income(self):
        url = reverse('case-list')
        data = {
            "detainee": self.detainee.detainee_id,
            "case_description": "Income too high",
            "predicted_case_type": "civil",
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
            "You are not eligible for this service due to income above 30000."
        )

    def test_get_case(self):
        case = Case.objects.create(
            detainee=self.detainee,
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
