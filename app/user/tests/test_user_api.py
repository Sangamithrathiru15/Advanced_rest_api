from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """test the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Tests creating user with valid payload is successful"""
        payload = {
            'email': 'test1@gmail.com',
            'password': 'testpass1',
            'name': 'Test1 Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        print(res.data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        print(user)
        self.assertFalse(user.check_password('testpass1'))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """tests creating user already exists"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """password must be more than 5 chars"""
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """tests that the token is created for he user"""
        payload = {'email': 'test@gmail.com', 'password': 'testpass'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_crate_token_invalid_credetials(self):
        """tests that the token is not created for the invalid creds"""
        create_user(email='test@gmail.com', password='test123')
        payload = {'email': 'test@gmail.com', 'password': 'testps'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """tests the token is not created for the user that doesnot exists"""
        payload = {'email': 'test@gmail.com', 'password': 'testps'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """tests that the token is not created for the missing fields"""
        res = self.client.post(TOKEN_URL, {
            'email': 'test@gmail.com',
            'password': ''
            })

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorised(self):
        """tests the authenticatio is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """test AP requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test1@gmail.com',
            password='testpass1',
            name='Test1 Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retrieving profile for loggedin user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """tests that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """test updating the user profile for authenticated user"""
        payload = {'name': 'Testnew Name', 'password': 'testps'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        # self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
