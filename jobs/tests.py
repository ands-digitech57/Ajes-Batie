from django.test import TestCase
from django.contrib.auth.models import User
from profiles.models import Profile
from .models import JobOffer, Application


class ApplicationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='applicant', password='pwd')
        self.job = JobOffer.objects.create(
            title='Dev', description='desc', company_name='Co', recruiter_name='HR', recruiter_phone='123'
        )
        self.profile = Profile.objects.create(user=self.user, email=self.user.email)

    def test_prevent_duplicate_application(self):
        Application.objects.create(job_offer=self.job, profile=self.profile)
        # second should raise IntegrityError if attempted via model
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Application.objects.create(job_offer=self.job, profile=self.profile)
from django.test import TestCase

# Create your tests here.
