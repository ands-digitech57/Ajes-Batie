from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User


class SignupTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('accounts:signup')

    def test_signup_creates_user_and_profile(self):
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'strong-password-123',
            'password2': 'strong-password-123',
        }
        resp = self.client.post(self.signup_url, data)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_duplicate_email_rejected(self):
        User.objects.create_user(username='existing', email='dup@example.com', password='x')
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'dup@example.com',
            'password1': 'another-pass-123',
            'password2': 'another-pass-123',
        }
        resp = self.client.post(self.signup_url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Un compte avec cet email existe deja.', resp.content.decode())

    def test_cv_too_large_rejected(self):
        # create a large dummy file (~11MB)
        large_content = b'a' * (11 * 1024 * 1024)
        cv = SimpleUploadedFile('cv.pdf', large_content, content_type='application/pdf')
        data = {
            'username': 'bigfile',
            'first_name': 'Big',
            'last_name': 'File',
            'email': 'big@example.com',
            'password1': 'pass12345',
            'password2': 'pass12345',
            'cv_file': cv,
        }
        resp = self.client.post(self.signup_url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Le fichier est trop volumineux', resp.content.decode())

    def test_photo_file_invalid_extension_rejected(self):
        photo = SimpleUploadedFile('photo.txt', b'not-an-image', content_type='text/plain')
        data = {
            'username': 'badphoto',
            'first_name': 'Bad',
            'last_name': 'Photo',
            'email': 'badphoto@example.com',
            'password1': 'pass12345',
            'password2': 'pass12345',
            'photo_file': photo,
        }
        resp = self.client.post(self.signup_url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Extension de fichier non autorisee', resp.content.decode())
