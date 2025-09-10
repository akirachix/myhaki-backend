from django.test import TestCase
from cases.models import Detainee, Case
from cpd.models import CPDPoint
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model()
class MyTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass123")

    def test_example(self):
        self.assertTrue(self.user.is_authenticated)

class CPDPointModelTest(TestCase):
    def setUp(self):
        self.detainee = Detainee.objects.create(
            first_name='John',
            last_name='Doe',
            id_number='ID56789',
            gender='male',
            relation_to_applicant='family'
        )
        self.case = Case.objects.create(
            detainee=self.detainee,
            case_description='Test Case for CPDPoint',
            predicted_case_type='civil',
            predicted_urgency_level='high',
            latitude=1.2921,
            longitude=36.8219,
            monthly_income='less_than_30000',
            income_source='informal',
            stage='in_progress',
            status='pending'
        )
        self.cpd_point = CPDPoint.objects.create(
            case=self.case,
            description="Completed training #123",
            points_earned=1.0
        )

    def test_cpd_point_creation(self):
        self.assertIsNotNone(self.cpd_point.cpd_id)  
        self.assertEqual(self.cpd_point.description, "Completed training #123")
        self.assertEqual(self.cpd_point.points_earned, 1.0)
        self.assertIsNotNone(self.cpd_point.created_at) 
        self.assertIsNotNone(self.cpd_point.updated_at)

    def test_cpd_point_retrieval(self):
        retrieved_cpd = CPDPoint.objects.get(cpd_id=self.cpd_point.cpd_id)
        self.assertEqual(retrieved_cpd.cpd_id, self.cpd_point.cpd_id)
        self.assertEqual(retrieved_cpd.description, "Completed training #123")
        self.assertEqual(retrieved_cpd.points_earned, 1.0)
        self.assertEqual(retrieved_cpd.created_at, self.cpd_point.created_at)
        self.assertEqual(retrieved_cpd.updated_at, self.cpd_point.updated_at)

    def test_str_representation(self):
        expected_str = f"CPD {self.cpd_point.cpd_id} for Lawyer None - {self.cpd_point.points_earned} points"
        self.assertEqual(str(self.cpd_point), expected_str)
