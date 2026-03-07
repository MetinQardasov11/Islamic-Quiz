import json

from django.test import TestCase
from django.urls import reverse

from .models import User


class ProfileApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='member',
            email='member@example.com',
            password='test1234',
            first_name='Member',
            last_name='User',
        )

    def test_update_profile_endpoint(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('authentication:update_profile'),
            data=json.dumps({'name': 'Updated User', 'email': 'updated@example.com'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Updated')
