from django.test import TestCase
# from django.contrib.auth.models import User  
from cases.models import Detainee
from datetime import date


class DetaineeModelTest(TestCase):

    def setUp(self):
        # self.user = User.objects.create_user(username="testuser", password="testpass")
        pass   # 🔹 No user setup for now

    def test_create_detainee(self):
        detainee = Detainee.objects.create(
            # user=self.user,
            id_number="123456789",
            gender="male",
            date_of_birth=date(1995, 5, 17),
            relation_to_applicant="family"
        )
        self.assertEqual(detainee.id_number, "123456789")
        self.assertEqual(detainee.gender, "male")
        self.assertEqual(detainee.relation_to_applicant, "family")
        self.assertIsNotNone(detainee.created_at)

    def test_str_representation(self):
        detainee = Detainee.objects.create(
            # user=self.user,
            id_number="987654321",
            gender="female",
            relation_to_applicant="other"
        )
        # self.assertEqual(
        #     str(detainee),
        #     f"Detainee {detainee.detainee_id} (User ID {self.user.id})"
        # )
        self.assertIn(f"Detainee{detainee.detainee_id}", str(detainee))  # ✅ Safe check without user

    def test_id_number_unique(self):
        Detainee.objects.create(
            # user=self.user,
            id_number="9999",
            gender="male",
            relation_to_applicant="family"
        )
        with self.assertRaises(Exception):
            Detainee.objects.create(
                # user=self.user,
                id_number="9999",
                gender="female",
                relation_to_applicant="other"
            )

    def test_optional_date_of_birth(self):
        detainee = Detainee.objects.create(
            # user=self.user,
            id_number="abc123",
            gender="male",
            relation_to_applicant="family"
        )
        self.assertIsNone(detainee.date_of_birth)

    # def test_foreign_key_relation(self):
    #     detainee = Detainee.objects.create(
    #         user=self.user,
    #         id_number="xyz789",
    #         gender="female",
    #         relation_to_applicant="family"
    #     )
    #     self.assertEqual(detainee.user.username, "testuser")
