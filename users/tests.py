from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import LawyerProfile, LskAdminProfile, ApplicantProfile

User = get_user_model()

class CustomUserAndProfilesTestCase(TestCase):

    def setUp(self):
            
        self.user = User.objects.create_user(
     email="testuser@example.com",
        password="pass123",
        first_name="Test",
        last_name="User",
        role="lawyer"
    )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="adminpass",
            role="admin"
        )
        self.lawyer_profile = LawyerProfile.objects.create(
            user=self.user,
            profile_id="LP1001",
            practising_status="active",
            practice_number="PN12345",
        )
        self.lsk_admin_profile = LskAdminProfile.objects.create(
            lawyer=self.lawyer_profile
        )
        self.applicant_user = User.objects.create_user(
            email="applicant@example.com",
            first_name="Applicant",
            last_name="User",
            password="applicantpass",
            role="applicant"
        )
        self.applicant_profile = ApplicantProfile.objects.create(
            user=self.applicant_user
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertEqual(self.user.role, "lawyer")
        self.assertEqual(self.admin.email, "admin@example.com")
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.is_superuser)
        self.assertEqual(self.admin.role, "admin")

    def test_lawyer_profile(self):
        self.assertEqual(self.lawyer_profile.user, self.user)
        self.assertEqual(self.lawyer_profile.profile_id, "LP1001")
        self.assertEqual(self.lawyer_profile.practice_number, "PN12345")
        self.assertFalse(self.lawyer_profile.verified)

    def test_lsk_admin_profile(self):
        self.assertEqual(self.lsk_admin_profile.lawyer, self.lawyer_profile)

    def test_applicant_profile(self):
        self.assertEqual(self.applicant_profile.user, self.applicant_user)
        self.assertEqual(self.applicant_user.role, "applicant")
