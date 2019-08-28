
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
UPDATE_URL = reverse('user:update')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ tests the users API (public) """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ test creating user with valid payload is successful """

        payload = {
            'email': 'test@gmail.com',
            'password': 'testpassword123',
            'name': 'test name'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        """ test that attempting to create user that already exists will fail """
        payload = {'email':'test@gmail.com', 'password':'testpassword123'}
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ test that a password must have over 5 characters """
        payload = {'email':'test@gmail.com', 'password':'tpw'}
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """ test that a token is created for the user """
        payload = {'email':'test@gmail.com', 'password':'testpassword123'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ test that token is not created if invalid credentials are given """
        create_user(email='test@gmail.com', password='testpassword123')
        payload = {'email':'test@gmail.com', 'password':'wrong'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_token_no_user(self):
        """ test that token is not created if user doesn't exist """
        payload = {'email':'test@gmail.com', 'password':'wrong'}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """ test that email and password are required to generate token """

        response = self.client.post(TOKEN_URL, {'email':'nope', 'password':''})

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ test that authentication is required for users and ensure endpoints private """
        response = self.client.post(UPDATE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ test API requests that require authentication """

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='testpassword123',
            name='testname'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_successful(self):
        """ test retrieving the profile for a logged-in user """
        response = self.client.get(UPDATE_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_from_update_endpoint_not_allowed(self):
        """ test that POST requests arent allowed on the update url """
        response = self.client.post(UPDATE_URL, {})

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ test that updating the user profile for an authenticated user works """

        payload = {'name': 'updated name', 'password': 'updatedpassword'}
        response = self.client.patch(UPDATE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
