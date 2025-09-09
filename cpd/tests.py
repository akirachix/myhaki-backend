# from .models import CPDPoint

# class CPDPointModelTest(TestCase):
#     def setUp(self):
#         self.cpd_point = CPDPoint.objects.create(
#             description="Completed training #123",
#             points_earned=1.0
#         )

#     def test_cpd_point_creation(self):
#         self.assertIsNotNone(self.cpd_point.cpd_id)  
#         self.assertEqual(self.cpd_point.description, "Completed training #123")
#         self.assertEqual(self.cpd_point.points_earned, 1.0)
#         self.assertIsNotNone(self.cpd_point.created_at) 
#         self.assertIsNotNone(self.cpd_point.updated_at)

#     def test_cpd_point_retrieval(self):
#         retrieved_cpd = CPDPoint.objects.get(cpd_id=self.cpd_point.cpd_id)
#         self.assertEqual(retrieved_cpd.cpd_id, self.cpd_point.cpd_id)
#         self.assertEqual(retrieved_cpd.description, "Completed training #123")
#         self.assertEqual(retrieved_cpd.points_earned, 1.0)
#         self.assertEqual(retrieved_cpd.created_at, self.cpd_point.created_at)
#         self.assertEqual(retrieved_cpd.updated_at, self.cpd_point.updated_at)


from django.test import TestCase
from cases.models import Detainee, Case
from cpd.models import CPDPoint
from django.utils import timezone



class CPDPointModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Create necessary related objects once
        cls.detainee = Detainee.objects.create(
            first_name='John',
            last_name='Doe',
            id_number='ID56789',
            gender='male',
            relation_to_applicant='family'
        )
        cls.case = Case.objects.create(
            detainee=cls.detainee,
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

    def setUp(self):
        # Create fresh object for each test
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
