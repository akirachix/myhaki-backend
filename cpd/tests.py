from django.test import TestCase
from .models import CPDPoint
from django.utils import timezone

class CPDPointModelTest(TestCase):
    def setUp(self):
        self.cpd_point = CPDPoint.objects.create(
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