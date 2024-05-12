from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class AccountViewsTests(APITestCase):

    def test_create_account_assert_successful_create(self):

        url = reverse("register_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserModel.objects.count(), 1)
        self.assertEqual(UserModel.objects.get(email="testmail@test.com").email, "testmail@test.com")

    def test_create_account_assert_account_exists(self):
        UserModel.objects.create_user(email="testmail@test.com", password="testpassword")

        url = reverse("register_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(UserModel.objects.count(), 1)

    def test_login_account_assert_successful_login(self):
        """
        Ensure obtain a token by logging in.
        """

        user = UserModel.objects.create_user(email="testmail@test.com", password="testpassword")
        user.is_active = True
        user.save()

        url = reverse("login_api_view")
        data = {"email": "testmail@test.com", "password": "testpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)